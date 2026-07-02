from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from src.config import settings
from src.core.rate_limit import limiter
from src.core.url_safety import UnsafeURLError, validate_public_url
from src.features.metadata.schemas import MetadataRequest, MetadataResponse
from src.features.metadata.service import fetch_metadata

router = APIRouter(prefix="/api")


@router.post("/metadata", response_model=MetadataResponse)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def metadata(request: Request, body: MetadataRequest) -> MetadataResponse:
    try:
        await run_in_threadpool(validate_public_url, body.url)
    except UnsafeURLError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        return await fetch_metadata(body.url)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
