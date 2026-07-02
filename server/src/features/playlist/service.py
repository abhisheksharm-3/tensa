from __future__ import annotations

from pathlib import Path

from redis.asyncio import Redis

from src.engines.ytdlp import best_thumbnail, dump_playlist_json
from src.features.download.service import produce_download
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
    """Download one playlist entry; mechanically identical to a single download."""
    return await produce_download(redis, job_id, params, job_dir)
