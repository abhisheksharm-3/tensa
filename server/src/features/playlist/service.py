from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.engines.ytdlp import best_thumbnail, dump_playlist_json, run_ytdlp
from src.features.download.constants import AUDIO_QUALITY, DEFAULT_FORMAT, QUALITY_FORMAT_MAP
from src.features.playlist.schemas import PlaylistItem


async def fetch_playlist_info(url: str) -> tuple[str | None, list[PlaylistItem]]:
    """Fetch flat playlist metadata: the playlist title and its items (with thumbnails)."""
    entries = await dump_playlist_json(url)
    title = next(
        (
            e.get("playlist_title") or e.get("playlist")
            for e in entries
            if e.get("playlist_title") or e.get("playlist")
        ),
        None,
    )
    items = [
        PlaylistItem(
            id=entry.get("id", ""),
            title=entry.get("title", "Untitled"),
            duration=entry.get("duration"),
            thumbnail=best_thumbnail(entry),
        )
        for entry in entries
    ]
    return title, items


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
        embed_subs=params.get("embed_subs", False),
        sponsorblock=params.get("sponsorblock", False),
    )
