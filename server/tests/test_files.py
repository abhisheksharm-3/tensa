from src.core.files import create_job_dir, format_file_size, get_job_output_file


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


def test_get_job_output_file_returns_first_file(tmp_path):
    job_dir = create_job_dir("job-with-file", base=tmp_path)
    (job_dir / "video.mp4").write_bytes(b"fake")
    result = get_job_output_file(job_dir)
    assert result is not None
    assert result.name == "video.mp4"
