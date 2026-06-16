import pytest
from fastapi import HTTPException

from src.config import settings
from src.core.files import validate_input_path


def test_accepts_file_under_download_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "download_dir", tmp_path)
    upload = tmp_path / "uploads" / "abc"
    upload.mkdir(parents=True)
    target = upload / "clip.mp4"
    target.write_bytes(b"data")

    resolved = validate_input_path(str(target))
    assert resolved == target.resolve()


def test_rejects_traversal_outside_root(tmp_path, monkeypatch):
    root = tmp_path / "downloads"
    root.mkdir()
    monkeypatch.setattr(settings, "download_dir", root)
    secret = tmp_path / "secret.txt"
    secret.write_text("top secret")

    with pytest.raises(HTTPException) as exc:
        validate_input_path("../secret.txt")
    assert exc.value.status_code == 400


def test_rejects_absolute_path_outside_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "download_dir", tmp_path / "downloads")
    (tmp_path / "downloads").mkdir()
    with pytest.raises(HTTPException) as exc:
        validate_input_path("/etc/passwd")
    assert exc.value.status_code == 400


def test_rejects_missing_file(tmp_path, monkeypatch):
    root = tmp_path / "downloads"
    root.mkdir()
    monkeypatch.setattr(settings, "download_dir", root)
    with pytest.raises(HTTPException) as exc:
        validate_input_path("uploads/missing.mp4")
    assert exc.value.status_code == 404
