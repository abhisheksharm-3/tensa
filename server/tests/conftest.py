import pytest
from httpx import ASGITransport, AsyncClient

from src.core.rate_limit import limiter
from src.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    """Route-logic tests should not exercise the Redis-backed limiter; that is an integration concern."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
