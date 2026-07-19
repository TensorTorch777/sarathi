"""Redis client lifecycle."""

from redis.asyncio import Redis

from app.core.config import get_settings

_redis: Redis | None = None


async def init_redis(redis_url: str | None = None) -> Redis:
    """Create the shared async Redis client."""
    global _redis
    settings = get_settings()
    _redis = Redis.from_url(
        redis_url or settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await _redis.ping()
    return _redis


def get_redis() -> Redis:
    """Return the initialized Redis client."""
    if _redis is None:
        raise RuntimeError("Redis client is not initialized")
    return _redis


async def dispose_redis() -> None:
    """Close the shared Redis client."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
    _redis = None
