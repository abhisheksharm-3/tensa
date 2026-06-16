from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.engines.ytdlp import run_ytdlp
from src.features.download.constants import AUDIO_QUALITY, DEFAULT_FORMAT, QUALITY_FORMAT_MAP


async def produce_download(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    """Download a single URL with yt-dlp at the requested quality, returning the output file."""
    quality = params.get("quality", "best")
    fmt = QUALITY_FORMAT_MAP.get(quality, DEFAULT_FORMAT)
    return await run_ytdlp(
        url=params["url"],
        fmt=fmt,
        output_dir=job_dir,
        job_id=job_id,
        redis=redis,
        audio_only=quality == AUDIO_QUALITY,
        audio_format=params.get("audio_format", "mp3"),
        embed_subs=params.get("embed_subs", False),
        sponsorblock=params.get("sponsorblock", False),
    )
