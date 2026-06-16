from pydantic import BaseModel


class PlaylistInfoRequest(BaseModel):
    url: str


class PlaylistItem(BaseModel):
    id: str
    title: str
    duration: int | None
    thumbnail: str | None


class PlaylistInfoResponse(BaseModel):
    items: list[PlaylistItem]
    total: int
