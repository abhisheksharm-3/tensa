from pydantic_settings import BaseSettings, NoDecode
from pydantic import field_validator
from pathlib import Path
from typing import Annotated


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    # Async SQLAlchemy DSN for the durable job store. Default is a local file-based
    # SQLite database so the API/worker run without Postgres in development; set
    # DATABASE_URL to a postgresql+asyncpg://... DSN in production.
    database_url: str = "sqlite+aiosqlite:///./tensa.db"
    download_dir: Path = Path("./downloads")
    whisper_models_dir: Path = Path("./models")
    rate_limit_per_hour: int = 20
    # Honour X-Forwarded-For for the rate-limit key. Enable only when the app sits
    # behind a trusted proxy that sets a reliable XFF header, else clients could
    # spoof it. Off by default (direct client IP).
    trust_proxy_headers: bool = False
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    file_expiry_seconds: int = 300
    file_sweep_seconds: int = 1800

    # Worker scaling — ARQ concurrency per worker process and per-job wall-clock
    # ceiling. Run several worker containers with `docker compose up --scale
    # worker=N`; each honours its own max_jobs.
    worker_max_jobs: int = 4
    worker_job_timeout: int = 600

    # Disk safety: hard ceiling on a single yt-dlp download. A multi-GB "Best"
    # pull once filled the disk and crashed Docker. Passed to yt-dlp as
    # --max-filesize. Accepts yt-dlp size syntax (e.g. "4G", "500M").
    max_download_filesize: str = "4G"

    # Uploads
    max_upload_size: int = 2 * 1024 * 1024 * 1024  # 2 GiB
    upload_allowed_content_types: Annotated[list[str], NoDecode] = [
        "video/mp4",
        "video/quicktime",
        "video/x-matroska",
        "video/webm",
        "video/x-msvideo",
        "video/mpeg",
        "audio/mpeg",
        "audio/mp4",
        "audio/x-m4a",
        "audio/wav",
        "audio/x-wav",
        "audio/flac",
        "audio/ogg",
        "audio/aac",
    ]

    # Observability
    log_level: str = "INFO"
    log_json: bool = True
    metrics_enabled: bool = True

    # YouTube hardening (other platforms need none of this).
    # Path to a Netscape-format cookies.txt — authenticates, raises rate limits,
    # unlocks age/region-locked videos.
    youtube_cookies_file: Path | None = None
    # Comma-separated yt-dlp player clients (e.g. "tv,web_safari"). Empty = let
    # yt-dlp choose its current default, which tracks YouTube's changes.
    youtube_player_clients: str = ""
    # Explicit PO token escape hatch ("<client>+<token>"). Usually unnecessary if
    # the bgutil PO-token provider plugin is installed (see server README).
    youtube_po_token: str | None = None
    # Base URL of the bgutil PO-token provider HTTP server (the sidecar). When set,
    # yt-dlp's bgutil plugin fetches PO tokens from it automatically, clearing
    # YouTube's "confirm you're not a bot" wall without manual cookies/tokens.
    youtube_pot_provider_url: str = ""

    @field_validator("download_dir", "whisper_models_dir", mode="before")
    @classmethod
    def make_path(cls, v: str) -> Path:
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @field_validator("cors_origins", "upload_allowed_content_types", mode="before")
    @classmethod
    def split_csv(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("youtube_cookies_file", "youtube_po_token", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        # docker-compose passes these as empty strings when unset; an empty
        # string for a Path field would resolve to Path("."), which yt-dlp then
        # tries to read as a cookies file. Treat blank as truly unset.
        if isinstance(v, str) and not v.strip():
            return None
        return v

    model_config = {"env_file": ".env"}


settings = Settings()
