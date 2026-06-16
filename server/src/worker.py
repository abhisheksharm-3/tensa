from __future__ import annotations

from arq import cron
from arq.connections import RedisSettings

from src.config import settings
from src.core.files import sweep_old_downloads
from src.core.redis import close_redis, get_redis
from src.features.audio.task import run_audio_extract
from src.features.convert.task import run_convert
from src.features.download.task import run_download
from src.features.playlist.task import run_playlist_item
from src.features.transcribe.task import run_transcribe


async def on_startup(ctx: dict) -> None:
    ctx["redis"] = await get_redis()


async def on_shutdown(ctx: dict) -> None:
    await close_redis()


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
    max_jobs = 4
    job_timeout = 600
    keep_result = 3600
