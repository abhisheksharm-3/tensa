from __future__ import annotations

import uuid

from src.core.logging import get_logger
from src.core.redis import get_arq_pool, publish_event
from src.jobs.constants import TASK_MAP
from src.jobs.schemas import JobRequest, JobStatus
from src.jobs.store import create_job_record, get_job_record, update_job_status

logger = get_logger(__name__)

_TERMINAL_STATUSES = {"done", "failed", "cancelled"}


async def enqueue_job(req: JobRequest) -> str:
    """Persist a pending job record and enqueue it on the shared ARQ pool."""
    job_id = str(uuid.uuid4())
    await create_job_record(job_id, req.type, req.model_dump(mode="json"))

    arq = await get_arq_pool()
    await arq.enqueue_job(TASK_MAP[req.type], job_id, req.model_dump(mode="json"), _job_id=job_id)
    logger.info("job.enqueued", job_id=job_id, type=req.type)
    return job_id


async def fetch_job_status(job_id: str) -> JobStatus | None:
    return await get_job_record(job_id)


async def cancel_job(job_id: str) -> bool:
    """Cancel a job: abort the ARQ job (stops the running worker coroutine, whose
    finally-blocks kill yt-dlp/ffmpeg) and mark it cancelled in Postgres."""
    status = await get_job_record(job_id)
    if status is None:
        return False
    if status.status in _TERMINAL_STATUSES:
        # Already finished; don't clobber the terminal state.
        return True

    arq = await get_arq_pool()
    from arq.jobs import Job as ArqJob

    arq_job = ArqJob(job_id, arq)
    # abort_job=True signals a queued job to drop and a running job to receive
    # CancelledError; we don't block on the result here.
    try:
        await arq_job.abort(timeout=0)
    except Exception as exc:  # best-effort; status still flips to cancelled
        logger.warning("job.abort_failed", job_id=job_id, error=str(exc))

    await update_job_status(job_id, {"status": "cancelled", "message": "Job cancelled"})
    await publish_event(job_id, {"type": "cancelled"})
    logger.info("job.cancelled", job_id=job_id)
    return True
