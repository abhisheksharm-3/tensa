from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from src.config import settings
from src.core.rate_limit import limiter
from src.core.url_safety import UnsafeURLError, validate_public_url
from src.features.playlist.schemas import PlaylistInfoRequest, PlaylistInfoResponse
from src.features.playlist.service import fetch_playlist_info

router = APIRouter(prefix="/api")


@router.post("/playlist/info", response_model=PlaylistInfoResponse)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def playlist_info(request: Request, body: PlaylistInfoRequest) -> PlaylistInfoResponse:
    try:
        await run_in_threadpool(validate_public_url, body.url)
    except UnsafeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        title, items = await fetch_playlist_info(body.url)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PlaylistInfoResponse(title=title, items=items, total=len(items))
