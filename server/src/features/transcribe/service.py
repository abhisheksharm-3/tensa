from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.core.redis import publish_event
from src.engines.whisper import run_whisper
from src.engines.ytdlp import run_ytdlp
from src.features.transcribe.constants import (
    FETCH_PROGRESS,
    SOURCE_AUDIO_FORMAT,
    SOURCE_AUDIO_SELECTOR,
    TRANSCRIBE_PROGRESS,
)


async def _resolve_audio(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    url = params.get("url")
    if not url:
        return Path(params["input_path"])
    await publish_event(job_id, FETCH_PROGRESS)
    return await run_ytdlp(
        url=url,
        fmt=SOURCE_AUDIO_SELECTOR,
        output_dir=job_dir,
        job_id=job_id,
        redis=redis,
        audio_only=True,
        audio_format=SOURCE_AUDIO_FORMAT,
    )


async def produce_transcript(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    """Resolve audio (download if a URL), then transcribe it with Whisper."""
    audio_file = await _resolve_audio(redis, job_id, params, job_dir)
    await publish_event(job_id, TRANSCRIBE_PROGRESS)
    return await run_whisper(
        audio_path=audio_file,
        output_dir=job_dir,
        model=params.get("whisper_model", "base"),
        language=params.get("language"),
        output_format=params.get("transcript_format", "srt"),
    )
