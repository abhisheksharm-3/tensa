from __future__ import annotations

from src.core.job_execution import execute_job
from src.features.playlist.service import produce_playlist_item


async def run_playlist_item(ctx: dict, job_id: str, params: dict) -> None:
    redis = ctx["redis"]
    await execute_job(job_id, lambda job_dir: produce_playlist_item(redis, job_id, params, job_dir))
