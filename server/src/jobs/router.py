from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from src.config import settings
from src.core.files import resolve_job_file, save_upload
from src.core.rate_limit import limiter
from src.core.sse import sse_response
from src.jobs.schemas import JobRequest, JobResponse, JobStatus, UploadResponse
from src.jobs.service import cancel_job, enqueue_job, fetch_job_status

router = APIRouter(prefix="/api")


@router.post("/jobs", response_model=JobResponse)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def create_job(request: Request, body: JobRequest) -> JobResponse:
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
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    dest = save_upload(file)
    return UploadResponse(upload_path=str(dest))
