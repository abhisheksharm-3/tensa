import json
from collections.abc import AsyncGenerator
from fastapi import Request
from fastapi.responses import StreamingResponse
from src.core.redis import get_redis


async def job_event_stream(job_id: str, request: Request) -> AsyncGenerator[str, None]:
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"job:{job_id}")
    try:
        yield ": keepalive\n\n"
        async for message in pubsub.listen():
            if await request.is_disconnected():
                break
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
