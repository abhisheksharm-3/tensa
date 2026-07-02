from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from src.config import settings
from src.core.files import create_job_dir, schedule_deletion
from src.core.logging import bind_job, clear_job_context, get_logger
from src.core.metrics import record_job
from src.core.redis import publish_event
from src.jobs.store import update_job_status

logger = get_logger(__name__)

ProduceOutput = Callable[[Path], Awaitable[Path]]

# Hold strong refs so fire-and-forget cleanup tasks aren't garbage-collected mid-flight.
_cleanup_tasks: set[asyncio.Task] = set()


async def execute_job(job_id: str, produce_output: ProduceOutput, job_type: str = "unknown") -> None:
    """Run a feature's work inside the standard job lifecycle.

    Marks the job running, invokes ``produce_output`` to generate the result file,
    then persists completion (Postgres) and publishes progress (Redis), scheduling
    cleanup. On failure it records the error and re-raises so ARQ marks the job
    failed. On cancellation/timeout it records the terminal state and re-raises so
    ``produce_output``'s ``finally`` can kill any child subprocess.
    """
    bind_job(job_id, job_type=job_type)
    logger.info("job.started")
    await update_job_status(job_id, {"status": "running", "type": job_type})
    record_job(job_type, "running")
    job_dir = create_job_dir(job_id)
    try:
        output_file = await produce_output(job_dir)
        download_url = f"/api/files/{job_id}/{output_file.name}"
        file_size = output_file.stat().st_size
        await update_job_status(
            job_id,
            {"status": "done", "download_url": download_url, "file_size": file_size},
        )
        await publish_event(job_id, {"type": "done", "download_url": download_url, "size": file_size})
        record_job(job_type, "done")
        logger.info("job.done", file_size=file_size)
        task = asyncio.create_task(schedule_deletion(job_dir, settings.file_expiry_seconds))
        _cleanup_tasks.add(task)
        task.add_done_callback(_cleanup_tasks.discard)
    except asyncio.CancelledError:
        await update_job_status(job_id, {"status": "cancelled", "message": "Job cancelled"})
        await publish_event(job_id, {"type": "cancelled"})
        record_job(job_type, "cancelled")
        logger.warning("job.cancelled")
        raise
    except Exception as exc:
        message = str(exc)
        await update_job_status(job_id, {"status": "failed", "message": message, "error": message})
        await publish_event(job_id, {"type": "error", "message": message})
        record_job(job_type, "failed")
        logger.error("job.failed", error=message)
        raise
    finally:
        clear_job_context()
