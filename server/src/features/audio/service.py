from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.core.redis import publish_event
from src.engines.ffmpeg import run_ffmpeg
from src.engines.ytdlp import run_ytdlp
from src.features.audio.constants import (
    BITRATE_FORMAT_MAP,
    DEFAULT_BITRATE_FORMAT,
    DEFAULT_CODEC,
    FORMAT_CODEC_MAP,
)


def _build_extract_args(input_path: Path, output_path: Path, audio_format: str, bitrate: str) -> list[str]:
    codec = FORMAT_CODEC_MAP.get(audio_format, DEFAULT_CODEC)
    return ["-y", "-i", str(input_path), "-vn", "-acodec", codec, "-ab", bitrate, str(output_path)]


async def produce_audio(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    """Extract audio from a URL (via yt-dlp) or an uploaded file (via ffmpeg)."""
    audio_format = params.get("audio_format", "mp3")
    bitrate = params.get("audio_bitrate", "192k")
    url = params.get("url")

    if url:
        fmt = BITRATE_FORMAT_MAP.get(bitrate, DEFAULT_BITRATE_FORMAT)
        return await run_ytdlp(
            url=url,
            fmt=fmt,
            output_dir=job_dir,
            job_id=job_id,
            redis=redis,
            audio_only=True,
            audio_format=audio_format,
        )

    input_path = Path(params["input_path"])
    output_file = job_dir / f"{input_path.stem}.{audio_format}"
    await run_ffmpeg(_build_extract_args(input_path, output_file, audio_format, bitrate))
    await publish_event(job_id, {"type": "progress", "percent": 100.0, "speed": "—", "eta": "done"})
    return output_file
