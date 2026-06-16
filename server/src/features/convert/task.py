from __future__ import annotations

from src.core.job_execution import execute_job
from src.features.convert.service import produce_convert


async def run_convert(ctx: dict, job_id: str, params: dict) -> None:
    redis = ctx["redis"]
    await execute_job(
        job_id, lambda job_dir: produce_convert(redis, job_id, params, job_dir), job_type="convert"
    )
