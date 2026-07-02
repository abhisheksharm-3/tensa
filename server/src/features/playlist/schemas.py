from __future__ import annotations

from pydantic import BaseModel


class PlaylistInfoRequest(BaseModel):
    url: str


class PlaylistItem(BaseModel):
    id: str
    title: str
    duration: int | None
    thumbnail: str | None


class PlaylistInfoResponse(BaseModel):
    title: str | None = None
    items: list[PlaylistItem]
    total: int
