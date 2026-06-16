from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    download_dir: Path = Path("./downloads")
    whisper_models_dir: Path = Path("./models")
    rate_limit_per_hour: int = 20
    cors_origins: list[str] = ["http://localhost:3000"]
    file_expiry_seconds: int = 300
    file_sweep_seconds: int = 1800

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

    @field_validator("download_dir", "whisper_models_dir", mode="before")
    @classmethod
    def make_path(cls, v: str) -> Path:
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {"env_file": ".env"}


settings = Settings()
