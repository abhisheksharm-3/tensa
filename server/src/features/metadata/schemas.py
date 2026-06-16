from pydantic import BaseModel


class MetadataRequest(BaseModel):
    url: str


class MetadataResponse(BaseModel):
    title: str
    thumbnail: str | None = None
    duration: int | None = None
    uploader: str | None = None
    is_playlist: bool = False
    entry_count: int | None = None
