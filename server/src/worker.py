from __future__ import annotations

from arq import cron
from arq.connections import RedisSettings

from src.config import settings
from src.core.db import dispose_db, init_db
from src.core.files import sweep_old_downloads
from src.core.logging import configure_logging, get_logger
from src.core.redis import close_redis, get_redis
from src.features.audio.task import run_audio_extract
from src.features.convert.task import run_convert
from src.features.download.task import run_download
from src.features.playlist.task import run_playlist_item
from src.features.transcribe.task import run_transcribe

logger = get_logger(__name__)


async def on_startup(ctx: dict) -> None:
    configure_logging()
    await init_db()
    ctx["redis"] = await get_redis()
    logger.info("worker.started", max_jobs=settings.worker_max_jobs)


async def on_shutdown(ctx: dict) -> None:
    await close_redis()
    await dispose_db()
    logger.info("worker.stopped")


async def sweep_downloads(ctx: dict) -> None:
    await sweep_old_downloads(settings.file_sweep_seconds)


class WorkerSettings:
    functions = [
        run_download,
        run_playlist_item,
        run_audio_extract,
        run_convert,
        run_transcribe,
    ]
    cron_jobs = [cron(sweep_downloads, minute={0, 30})]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = on_startup
    on_shutdown = on_shutdown
    # Concurrency and per-job ceiling are configurable so several worker
    # containers can be scaled out: `docker compose up --scale worker=N`.
    max_jobs = settings.worker_max_jobs
    job_timeout = settings.worker_job_timeout
    keep_result = 3600
    # Enables Job.abort() so the API can really cancel a running job (its
    # CancelledError unwinds into the engine finally-blocks that kill subprocesses).
    allow_abort_jobs = True
