from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.core.db import dispose_db, init_db
from src.core.logging import configure_logging, get_logger
from src.core.metrics import setup_metrics
from src.core.rate_limit import limiter
from src.core.redis import close_redis, get_arq_pool
from src.features.metadata.router import router as metadata_router
from src.features.playlist.router import router as playlist_router
from src.jobs.router import router as jobs_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    # Build the ARQ pool once and reuse for every enqueue (no per-request churn).
    app.state.arq = await get_arq_pool()
    logger.info("api.started")
    yield
    await close_redis()
    await dispose_db()
    logger.info("api.stopped")


app = FastAPI(title="Tensa", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,  # no cookies/auth are used, so credentialed CORS is unnecessary
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_metrics(app)

app.include_router(jobs_router)
app.include_router(playlist_router)
app.include_router(metadata_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
