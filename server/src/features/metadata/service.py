from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from src.engines.ytdlp import best_thumbnail, dump_video_metadata, is_youtube
from src.features.metadata.schemas import MetadataResponse


def _youtube_id(url: str) -> str | None:
    """Extract a YouTube video id from a watch/short/youtu.be URL, if present."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if host.endswith("youtu.be"):
        return parts.path.lstrip("/").split("/")[0] or None
    if "youtube" in host:
        if parts.path.startswith(("/shorts/", "/embed/", "/v/")):
            return parts.path.split("/")[2] if len(parts.path.split("/")) > 2 else None
        vid = parse_qs(parts.query).get("v")
        return vid[0] if vid else None
    return None


async def fetch_metadata(url: str) -> MetadataResponse:
    """Resolve any media URL to a title/thumbnail/duration, for single items and playlists.

    Falls back to a synthesized YouTube thumbnail when extraction is blocked (e.g.
    YouTube's anti-bot check) so the UI still gets a cover image.
    """
    try:
        data = await dump_video_metadata(url)
    except RuntimeError:
        vid = _youtube_id(url) if is_youtube(url) else None
        if vid:
            return MetadataResponse(
                title="YouTube video",
                thumbnail=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                is_playlist=False,
            )
        raise
    is_playlist = data.get("_type") == "playlist" or "entries" in data

    if is_playlist:
        entries = [e for e in (data.get("entries") or []) if isinstance(e, dict)]
        thumbnail = best_thumbnail(data) or (best_thumbnail(entries[0]) if entries else None)
        return MetadataResponse(
            title=data.get("title") or "Playlist",
            thumbnail=thumbnail,
            uploader=data.get("uploader") or data.get("channel"),
            is_playlist=True,
            entry_count=data.get("playlist_count") or (len(entries) or None),
        )

    return MetadataResponse(
        title=data.get("title") or "Untitled",
        thumbnail=best_thumbnail(data),
        duration=data.get("duration"),
        uploader=data.get("uploader") or data.get("channel"),
        is_playlist=False,
    )
