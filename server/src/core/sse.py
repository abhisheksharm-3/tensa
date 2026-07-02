import json
from collections.abc import AsyncGenerator
from fastapi import Request
from fastapi.responses import StreamingResponse
from src.core.redis import get_redis
from src.jobs.store import get_job_record

_TERMINAL_STATUSES = ("done", "failed", "cancelled")
_KEEPALIVE_INTERVAL = 15.0


def _terminal_event(status) -> dict:
    """Mirror the event shape execute_job publishes for each terminal state."""
    if status.status == "done":
        return {"type": "done", "download_url": status.download_url, "size": status.file_size}
    if status.status == "failed":
        return {"type": "error", "message": status.error or status.message}
    return {"type": "cancelled"}


async def job_event_stream(job_id: str, request: Request) -> AsyncGenerator[str, None]:
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"job:{job_id}")
    try:
        yield ": keepalive\n\n"
        # Subscribe first, then read durable state: a job that finished before the
        # client subscribed would otherwise hang forever waiting on pub/sub.
        record = await get_job_record(job_id)
        if record is not None and record.status in _TERMINAL_STATUSES:
            yield f"data: {json.dumps(_terminal_event(record))}\n\n"
            return
        while True:
            if await request.is_disconnected():
                break
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=_KEEPALIVE_INTERVAL
            )
            if message is None:
                yield ": keepalive\n\n"
                continue
            if message["type"] != "message":
                continue
            data = message["data"]
            payload = data.decode() if isinstance(data, bytes) else data
            yield f"data: {payload}\n\n"
            try:
                event = json.loads(payload)
                if event.get("type") in ("done", "error", "cancelled"):
                    break
            except (json.JSONDecodeError, AttributeError):
                pass
    finally:
        await pubsub.unsubscribe(f"job:{job_id}")
        await pubsub.aclose()


def sse_response(job_id: str, request: Request) -> StreamingResponse:
    return StreamingResponse(
        job_event_stream(job_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
