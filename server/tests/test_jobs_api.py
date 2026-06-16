from unittest.mock import AsyncMock, patch

import pytest

from src.jobs.schemas import JobStatus


@pytest.mark.anyio
async def test_create_job_returns_job_id(client):
    with patch("src.jobs.router.enqueue_job", new_callable=AsyncMock) as mock_enqueue:
        mock_enqueue.return_value = "test-job-123"
        resp = await client.post(
            "/api/jobs",
            json={"type": "download", "url": "https://youtube.com/watch?v=x", "quality": "best"},
        )
    assert resp.status_code == 200
    assert resp.json()["job_id"] == "test-job-123"


@pytest.mark.anyio
async def test_get_job_not_found(client):
    with patch("src.jobs.router.fetch_job_status", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = None
        resp = await client.get("/api/jobs/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_get_job_found(client):
    with patch("src.jobs.router.fetch_job_status", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = JobStatus(job_id="abc", status="running")
        resp = await client.get("/api/jobs/abc")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


@pytest.mark.anyio
async def test_delete_job_not_found(client):
    with patch("src.jobs.router.cancel_job", new_callable=AsyncMock) as mock_cancel:
        mock_cancel.return_value = False
        resp = await client.delete("/api/jobs/ghost")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_delete_job_success(client):
    with patch("src.jobs.router.cancel_job", new_callable=AsyncMock) as mock_cancel:
        mock_cancel.return_value = True
        resp = await client.delete("/api/jobs/real-job")
    assert resp.status_code == 204


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
