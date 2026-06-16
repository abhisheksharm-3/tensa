from __future__ import annotations

import json

from src.core.db import get_sessionmaker
from src.core.logging import get_logger
from src.jobs.models import Job
from src.jobs.schemas import JobStatus

logger = get_logger(__name__)

# Columns that map 1:1 from a status dict onto the Job row.
_STATUS_FIELDS = ("status", "message", "download_url", "file_size", "error")


async def create_job_record(job_id: str, job_type: str, params: dict) -> None:
    """Insert the initial pending record. Idempotent on the primary key."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        async with session.begin():
            session.add(
                Job(
                    id=job_id,
                    type=job_type,
                    status="pending",
                    params=json.dumps(params),
                )
            )


async def update_job_status(job_id: str, fields: dict) -> None:
    """Upsert status fields onto a job row.

    Workers may process a job whose row predates this code path; upserting keeps
    status durable even then. ``type`` is required only on first insert and
    defaults to "unknown" if the row is missing.
    """
    updates = {k: v for k, v in fields.items() if k in _STATUS_FIELDS}
    if not updates:
        return
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        async with session.begin():
            existing = await session.get(Job, job_id)
            if existing is None:
                session.add(
                    Job(id=job_id, type=fields.get("type", "unknown"), **updates)
                )
                return
            for key, value in updates.items():
                setattr(existing, key, value)


async def get_job_record(job_id: str) -> JobStatus | None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        row = await session.get(Job, job_id)
        if row is None:
            return None
        return JobStatus(
            job_id=row.id,
            status=row.status,
            message=row.message,
            download_url=row.download_url,
            file_size=row.file_size,
            error=row.error,
            type=row.type,
        )
