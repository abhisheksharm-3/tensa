from __future__ import annotations

import json

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool
from redis.asyncio import Redis

from src.config import settings

_client: Redis | None = None
_arq_pool: ArqRedis | None = None


async def get_redis() -> Redis:
    """Shared Redis client for pub/sub progress and slowapi storage."""
    global _client
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=False)
    return _client


async def get_arq_pool() -> ArqRedis:
    """Shared ARQ pool, built once and reused for every enqueue (no per-request churn)."""
    global _arq_pool
    if _arq_pool is None:
        _arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return _arq_pool


async def close_redis() -> None:
    global _client, _arq_pool
    if _client:
        await _client.aclose()
        _client = None
    if _arq_pool:
        await _arq_pool.aclose()
        _arq_pool = None


async def publish_event(job_id: str, event: dict) -> None:
    r = await get_redis()
    await r.publish(f"job:{job_id}", json.dumps(event))
