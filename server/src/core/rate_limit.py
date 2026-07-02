from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from src.config import settings


def client_key(request: Request) -> str:
    """Rate-limit key: the real client IP.

    get_remote_address alone collapses every client to the proxy IP behind a
    reverse proxy. When trust_proxy_headers is set we take the first hop of
    X-Forwarded-For (the originating client) instead.
    """
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# swallow_errors is a deliberate fail-open: Redis is critical infra here (job
# enqueue, ARQ and pub/sub all require it), so if Redis is down the app is already
# degraded and enqueue fails anyway — failing closed would only lock out the
# legitimate operator of this self-hosted tool without adding real protection.
limiter = Limiter(
    key_func=client_key,
    storage_uri=settings.redis_url,
    swallow_errors=True,
)
