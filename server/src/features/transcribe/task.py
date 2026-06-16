from __future__ import annotations

from src.core.job_execution import execute_job
from src.features.transcribe.service import produce_transcript


async def run_transcribe(ctx: dict, job_id: str, params: dict) -> None:
    redis = ctx["redis"]
    await execute_job(job_id, lambda job_dir: produce_transcript(redis, job_id, params, job_dir))
