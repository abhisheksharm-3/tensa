from __future__ import annotations

import asyncio
import shutil
import time
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from src.config import settings

# yt-dlp / ffmpeg leave these behind mid-flight or as sidecars; never select them
# as the job's output file.
_TRANSIENT_SUFFIXES = {".part", ".ytdl", ".tmp"}
_SIDECAR_SUFFIXES = {".info.json", ".description", ".annotations.xml"}

_UPLOAD_CHUNK = 1024 * 1024  # 1 MiB


def create_job_dir(job_id: str, base: Path | None = None) -> Path:
    root = base or settings.download_dir
    job_dir = root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def _is_output_candidate(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix in _TRANSIENT_SUFFIXES:
        return False
    name = path.name
    if any(name.endswith(suffix) for suffix in _SIDECAR_SUFFIXES):
        return False
    return True


def get_job_output_file(job_dir: Path) -> Path | None:
    """Pick the real output file, ignoring partial/sidecar artifacts.

    yt-dlp can leave .part/.ytdl/.info.json alongside the finished media; choosing
    files[0] was nondeterministic. Prefer real candidates, newest by mtime.
    """
    candidates = [f for f in job_dir.iterdir() if _is_output_candidate(f)]
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)


async def save_upload(file: UploadFile) -> Path:
    """Stream an uploaded file to disk with aiofiles, enforcing size + content-type.

    Content-type is required and must be allow-listed; bytes are written in chunks
    and aborted (with cleanup) once the configured ceiling is exceeded, so a huge
    upload can't fill the disk before validation.
    """
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if not content_type:
        raise HTTPException(status_code=415, detail="Missing content type")
    if content_type not in settings.upload_allowed_content_types:
        raise HTTPException(status_code=415, detail=f"Unsupported content type: {content_type}")

    upload_dir = settings.download_dir / "uploads" / str(uuid.uuid4())
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / Path(file.filename or "upload").name

    written = 0
    try:
        async with aiofiles.open(dest, "wb") as out:
            while chunk := await file.read(_UPLOAD_CHUNK):
                written += len(chunk)
                if written > settings.max_upload_size:
                    raise HTTPException(status_code=413, detail="Upload exceeds maximum allowed size")
                await out.write(chunk)
    except HTTPException:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise
    return dest


def validate_input_path(input_path: str) -> Path:
    """Resolve a client-supplied input_path and constrain it under download_dir.

    Guards against arbitrary file reads (e.g. /etc/passwd): the resolved path must
    live under download_dir (covering both uploads/ and prior job outputs).
    """
    root = settings.download_dir.resolve()
    resolved = (root / input_path).resolve() if not Path(input_path).is_absolute() else Path(input_path).resolve()
    if not resolved.is_relative_to(root):
        raise HTTPException(status_code=400, detail="input_path is outside the allowed directory")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="input_path does not exist")
    return resolved


def resolve_job_file(job_id: str, filename: str) -> Path | None:
    """Resolve a served file path, guarding against path traversal. Returns None if missing.

    job_id must be a UUID, and the resolved path must stay under download_dir.
    """
    try:
        uuid.UUID(job_id)
    except ValueError:
        return None
    root = settings.download_dir.resolve()
    file_path = (root / job_id / Path(filename).name).resolve()
    if not file_path.is_relative_to(root):
        return None
    return file_path if file_path.is_file() else None


async def schedule_deletion(job_dir: Path, delay: int) -> None:
    await asyncio.sleep(delay)
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)


def _sweep_entry(entry: Path, now: float, max_age: int) -> None:
    if now - entry.stat().st_mtime <= max_age:
        return
    if entry.is_dir():
        shutil.rmtree(entry, ignore_errors=True)
    else:
        entry.unlink(missing_ok=True)


async def sweep_old_downloads(max_age: int) -> None:
    root = settings.download_dir
    if not root.exists():
        return
    now = time.time()
    for entry in root.iterdir():
        # uploads/ holds many independent uploads under one dir; age each out on
        # its own mtime so stale uploads expire and an active one isn't wiped.
        if entry.name == "uploads" and entry.is_dir():
            for upload in entry.iterdir():
                _sweep_entry(upload, now, max_age)
        else:
            _sweep_entry(entry, now, max_age)
