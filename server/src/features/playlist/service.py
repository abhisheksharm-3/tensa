from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.engines.ytdlp import dump_playlist_json, run_ytdlp
from src.features.download.constants import AUDIO_QUALITY, DEFAULT_FORMAT, QUALITY_FORMAT_MAP
from src.features.playlist.schemas import PlaylistItem


async def fetch_playlist_info(url: str) -> list[PlaylistItem]:
    """Fetch flat playlist metadata, mapping raw yt-dlp entries into playlist items."""
    entries = await dump_playlist_json(url)
    return [
        PlaylistItem(
            id=entry.get("id", ""),
            title=entry.get("title", "Untitled"),
            duration=entry.get("duration"),
            thumbnail=entry.get("thumbnail"),
        )
        for entry in entries
    ]


async def produce_playlist_item(redis: Redis, job_id: str, params: dict, job_dir: Path) -> Path:
    """Download one playlist entry; identical mechanics to a single download."""
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
    )
