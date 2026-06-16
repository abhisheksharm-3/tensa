from src.config import Settings


def test_settings_defaults(tmp_path):
    s = Settings(
        redis_url="redis://localhost:6379",
        download_dir=str(tmp_path / "downloads"),
        whisper_models_dir=str(tmp_path / "models"),
    )
    assert s.rate_limit_per_hour == 20
    assert s.cors_origins == ["http://localhost:3000"]
    assert s.file_expiry_seconds == 300
    assert s.file_sweep_seconds == 1800


def test_cors_origins_parsed_from_comma_string(tmp_path):
    s = Settings(
        download_dir=str(tmp_path / "d"),
        whisper_models_dir=str(tmp_path / "m"),
        cors_origins="http://localhost:3000, https://tensa.app",
    )
    assert s.cors_origins == ["http://localhost:3000", "https://tensa.app"]
