from __future__ import annotations

from src.core.job_execution import execute_job
from src.features.audio.service import produce_audio


async def run_audio_extract(ctx: dict, job_id: str, params: dict) -> None:
    redis = ctx["redis"]
    await execute_job(
        job_id, lambda job_dir: produce_audio(redis, job_id, params, job_dir), job_type="audio_extract"
    )
