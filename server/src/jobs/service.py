from __future__ import annotations

import uuid

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool

from src.config import settings
from src.core.redis import get_job_status, publish_event, set_job_status
from src.jobs.constants import TASK_MAP
from src.jobs.schemas import JobRequest, JobStatus


async def enqueue_job(req: JobRequest) -> str:
    job_id = str(uuid.uuid4())
    await set_job_status(job_id, {"job_id": job_id, "status": "pending"})

    arq: ArqRedis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await arq.enqueue_job(TASK_MAP[req.type], job_id, req.model_dump(), _job_id=job_id)
    finally:
        await arq.aclose()
    return job_id


async def fetch_job_status(job_id: str) -> JobStatus | None:
    data = await get_job_status(job_id)
    if data is None:
        return None
    return JobStatus(**data)


async def cancel_job(job_id: str) -> bool:
    status = await get_job_status(job_id)
    if status is None:
        return False
    await set_job_status(job_id, {**status, "status": "cancelled"})
    await publish_event(job_id, {"type": "cancelled"})
    return True
