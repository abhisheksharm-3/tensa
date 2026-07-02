from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from src.config import settings
from src.core.files import resolve_job_file, save_upload, validate_input_path
from src.core.rate_limit import limiter
from src.core.sse import sse_response
from src.core.url_safety import UnsafeURLError, validate_public_url
from src.jobs.schemas import JobRequest, JobResponse, JobStatus, UploadResponse
from src.jobs.service import cancel_job, enqueue_job, fetch_job_status

router = APIRouter(prefix="/api")

# Job types whose input_path points at a server-side file we must constrain.
_FILE_INPUT_TYPES = {"audio_extract", "convert", "transcribe"}


async def _validate_job_request(body: JobRequest) -> None:
    """Validate untrusted JobRequest fields: SSRF-guard the URL, constrain input_path."""
    if body.url:
        try:
            await run_in_threadpool(validate_public_url, body.url)
        except UnsafeURLError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    if body.input_path and body.type in _FILE_INPUT_TYPES:
        # Raises HTTPException on traversal / missing file; normalises the path.
        body.input_path = str(validate_input_path(body.input_path))


@router.post("/jobs", response_model=JobResponse)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def create_job(request: Request, body: JobRequest) -> JobResponse:
    await _validate_job_request(body)
    job_id = await enqueue_job(body)
    return JobResponse(job_id=job_id)


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str, request: Request):
    return sse_response(job_id, request)


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str) -> JobStatus:
    status = await fetch_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: str) -> None:
    if not await cancel_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")


@router.get("/files/{job_id}/{filename}")
async def serve_file(job_id: str, filename: str) -> FileResponse:
    file_path = resolve_job_file(job_id, filename)
    if file_path is None:
        raise HTTPException(status_code=404, detail="File expired or not found")
    return FileResponse(path=file_path, filename=file_path.name, media_type="application/octet-stream")


@router.post("/upload", response_model=UploadResponse)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def upload_file(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    dest = await save_upload(file)
    # Return a handle relative to download_dir, not the absolute container FS path.
    # validate_input_path resolves it back under the root when reused as input_path.
    return UploadResponse(upload_path=str(dest.relative_to(settings.download_dir)))
