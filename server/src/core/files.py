import asyncio
import shutil
import time
import uuid
from pathlib import Path

from fastapi import UploadFile

from src.config import settings


def create_job_dir(job_id: str, base: Path | None = None) -> Path:
    root = base or settings.download_dir
    job_dir = root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def get_job_output_file(job_dir: Path) -> Path | None:
    files = [f for f in job_dir.iterdir() if f.is_file()]
    return files[0] if files else None


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    for unit in units[:-1]:
        if value < 1024:
            return f"{value:.1f} {unit}" if unit != "B" else "0 B"
        value /= 1024
    return f"{value:.1f} TB"


def save_upload(file: UploadFile) -> Path:
    """Persist an uploaded file under a unique uploads subdirectory and return its path."""
    upload_dir = settings.download_dir / "uploads" / str(uuid.uuid4())
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / Path(file.filename or "upload").name
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return dest


def resolve_job_file(job_id: str, filename: str) -> Path | None:
    """Resolve a served file path, guarding against path traversal. Returns None if missing."""
    file_path = settings.download_dir / job_id / Path(filename).name
    return file_path if file_path.exists() else None


async def schedule_deletion(job_dir: Path, delay: int) -> None:
    await asyncio.sleep(delay)
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)


async def sweep_old_downloads(max_age: int) -> None:
    root = settings.download_dir
    if not root.exists():
        return
    now = time.time()
    for job_dir in root.iterdir():
        if job_dir.is_dir():
            age = now - job_dir.stat().st_mtime
            if age > max_age:
                shutil.rmtree(job_dir, ignore_errors=True)
