import asyncio
from pathlib import Path

import pytest

from src.config import settings
from src.core import job_execution


@pytest.fixture
def captured(monkeypatch, tmp_path):
    """Stub the DB/Redis/cleanup side effects and capture what execute_job emits."""
    monkeypatch.setattr(settings, "download_dir", tmp_path)
    statuses: list[dict] = []
    events: list[dict] = []
    cleanups: list[tuple] = []

    async def fake_update(job_id, fields):
        statuses.append(fields)

    async def fake_publish(job_id, event):
        events.append(event)

    async def fake_schedule(job_dir, delay):
        cleanups.append((job_dir, delay))

    monkeypatch.setattr(job_execution, "update_job_status", fake_update)
    monkeypatch.setattr(job_execution, "publish_event", fake_publish)
    monkeypatch.setattr(job_execution, "schedule_deletion", fake_schedule)
    return statuses, events, cleanups


@pytest.mark.anyio
async def test_execute_job_success_marks_running_then_done_and_schedules_cleanup(captured):
    statuses, events, cleanups = captured

    async def produce(job_dir: Path) -> Path:
        out = job_dir / "result.mp4"
        out.write_bytes(b"data")
        return out

    await job_execution.execute_job("job-1", produce, job_type="download")
    await asyncio.sleep(0)  # let the fire-and-forget cleanup task run

    assert statuses[0]["status"] == "running"
    assert statuses[-1]["status"] == "done"
    assert statuses[-1]["file_size"] == 4
    assert statuses[-1]["download_url"] == "/api/files/job-1/result.mp4"
    assert events[-1] == {"type": "done", "download_url": "/api/files/job-1/result.mp4", "size": 4}
    assert cleanups, "cleanup deletion should be scheduled"


@pytest.mark.anyio
async def test_execute_job_failure_records_failed_and_reraises(captured):
    statuses, events, _ = captured

    async def produce(job_dir: Path) -> Path:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await job_execution.execute_job("job-2", produce)

    assert statuses[-1]["status"] == "failed"
    assert statuses[-1]["message"] == "boom"
    assert events[-1] == {"type": "error", "message": "boom"}


@pytest.mark.anyio
async def test_execute_job_cancellation_records_cancelled_and_reraises(captured):
    statuses, events, _ = captured

    async def produce(job_dir: Path) -> Path:
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await job_execution.execute_job("job-3", produce)

    assert statuses[-1]["status"] == "cancelled"
    assert events[-1] == {"type": "cancelled"}
