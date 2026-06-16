import json
from redis.asyncio import Redis
from src.config import settings

_client: Redis | None = None


async def get_redis() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=False)
    return _client


async def close_redis() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def publish_event(job_id: str, event: dict) -> None:
    r = await get_redis()
    await r.publish(f"job:{job_id}", json.dumps(event))


async def set_job_status(job_id: str, status: dict, ttl: int = 3600) -> None:
    r = await get_redis()
    await r.setex(f"status:{job_id}", ttl, json.dumps(status))


async def get_job_status(job_id: str) -> dict | None:
    r = await get_redis()
    raw = await r.get(f"status:{job_id}")
    return json.loads(raw) if raw else None
