from fastapi import APIRouter, HTTPException

from src.features.playlist.schemas import PlaylistInfoRequest, PlaylistInfoResponse
from src.features.playlist.service import fetch_playlist_info

router = APIRouter(prefix="/api")


@router.post("/playlist/info", response_model=PlaylistInfoResponse)
async def playlist_info(body: PlaylistInfoRequest) -> PlaylistInfoResponse:
    try:
        items = await fetch_playlist_info(body.url)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return PlaylistInfoResponse(items=items, total=len(items))
