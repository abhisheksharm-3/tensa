from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from src.config import settings
from src.core.files import create_job_dir, schedule_deletion
from src.core.redis import publish_event, set_job_status

ProduceOutput = Callable[[Path], Awaitable[Path]]


async def execute_job(job_id: str, produce_output: ProduceOutput) -> None:
    """Run a feature's work inside the standard job lifecycle.

    Marks the job running, invokes ``produce_output`` to generate the result file,
    then publishes completion and schedules cleanup. On failure it marks the job
    failed, emits an error event, and re-raises so ARQ records the failure.
    """
    await set_job_status(job_id, {"job_id": job_id, "status": "running"})
    job_dir = create_job_dir(job_id)
    try:
        output_file = await produce_output(job_dir)
        download_url = f"/api/files/{job_id}/{output_file.name}"
        file_size = output_file.stat().st_size
        await set_job_status(
            job_id,
            {"job_id": job_id, "status": "done", "download_url": download_url, "file_size": file_size},
        )
        await publish_event(job_id, {"type": "done", "download_url": download_url, "size": file_size})
        asyncio.create_task(schedule_deletion(job_dir, settings.file_expiry_seconds))
    except Exception as exc:
        message = str(exc)
        await set_job_status(job_id, {"job_id": job_id, "status": "failed", "message": message})
        await publish_event(job_id, {"type": "error", "message": message})
        raise
