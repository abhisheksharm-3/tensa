from __future__ import annotations

from src.core.job_execution import execute_job
from src.features.download.service import produce_download


async def run_download(ctx: dict, job_id: str, params: dict) -> None:
    redis = ctx["redis"]
    await execute_job(job_id, lambda job_dir: produce_download(redis, job_id, params, job_dir))
