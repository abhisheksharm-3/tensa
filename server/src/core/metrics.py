from __future__ import annotations

import time

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

from src.config import settings

# Request metrics — labelled by method, templated path, and status code.
REQUEST_COUNT = Counter(
    "tensa_http_requests_total",
    "Total HTTP requests",
    labelnames=("method", "path", "status"),
)
REQUEST_LATENCY = Histogram(
    "tensa_http_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=("method", "path"),
)
# Job lifecycle counter, labelled for slicing by type and status.
JOBS_TOTAL = Counter(
    "tensa_jobs_total",
    "Count of job lifecycle transitions",
    labelnames=("type", "status"),
)


def record_job(job_type: str, status: str) -> None:
    JOBS_TOTAL.labels(type=job_type or "unknown", status=status).inc()


def _route_template(request: Request) -> str:
    """Use the matched route's template (e.g. /api/jobs/{job_id}) to bound cardinality."""
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


def setup_metrics(app: FastAPI) -> None:
    """Add request latency/count middleware and a /metrics endpoint.

    Uses prometheus_client directly (no route-introspection plugin) to stay
    compatible across FastAPI/Starlette versions.
    """
    if not settings.metrics_enabled:
        return

    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        path = _route_template(request)
        REQUEST_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
        REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
