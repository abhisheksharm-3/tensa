import os
import uuid

from src.config import settings
from src.core.files import (
    create_job_dir,
    format_file_size,
    get_job_output_file,
    resolve_job_file,
)


def test_format_file_size():
    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1_048_576) == "1.0 MB"
    assert format_file_size(142_000_000) == "135.4 MB"


def test_create_job_dir(tmp_path):
    job_dir = create_job_dir("test-job-123", base=tmp_path)
    assert job_dir.exists()
    assert job_dir.name == "test-job-123"


def test_get_job_output_file_returns_none_when_empty(tmp_path):
    job_dir = create_job_dir("empty-job", base=tmp_path)
    assert get_job_output_file(job_dir) is None


def test_get_job_output_file_returns_real_file(tmp_path):
    job_dir = create_job_dir("job-with-file", base=tmp_path)
    (job_dir / "video.mp4").write_bytes(b"fake")
    result = get_job_output_file(job_dir)
    assert result is not None
    assert result.name == "video.mp4"


def test_get_job_output_file_ignores_partial_and_sidecar(tmp_path):
    job_dir = create_job_dir("job-partials", base=tmp_path)
    real = job_dir / "video.mp4"
    real.write_bytes(b"done")
    (job_dir / "video.mp4.part").write_bytes(b"partial")
    (job_dir / "video.f137.ytdl").write_bytes(b"frag")
    (job_dir / "video.info.json").write_text("{}")
    # Make a transient file newest by mtime — it must still be skipped.
    os.utime(real, (1, 1))
    os.utime(job_dir / "video.mp4.part", None)

    result = get_job_output_file(job_dir)
    assert result is not None
    assert result.name == "video.mp4"


def test_resolve_job_file_rejects_non_uuid(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "download_dir", tmp_path)
    assert resolve_job_file("../../etc", "passwd") is None
    assert resolve_job_file("not-a-uuid", "file.mp4") is None


def test_resolve_job_file_accepts_uuid_within_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "download_dir", tmp_path)
    job_id = str(uuid.uuid4())
    job_dir = tmp_path / job_id
    job_dir.mkdir()
    (job_dir / "out.mp4").write_bytes(b"x")
    resolved = resolve_job_file(job_id, "out.mp4")
    assert resolved is not None
    assert resolved.name == "out.mp4"


def test_resolve_job_file_traversal_in_filename_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "download_dir", tmp_path)
    job_id = str(uuid.uuid4())
    (tmp_path / job_id).mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("s")
    # Path(filename).name strips directory components, so traversal can't escape.
    assert resolve_job_file(job_id, "../../secret.txt") is None
