import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    """Returns an async Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Closes the Redis client pool."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception:
            pass
        _redis_client = None


async def get_cached_json(key: str) -> Optional[dict]:
    """Retrieve and parse cached JSON data safely."""
    try:
        client = get_redis()
        data = await client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis get error: {e}")
    return None


async def set_cached_json(key: str, data: Any, expire_seconds: int = 300) -> None:
    """Serialize and save data to Redis with a TTL."""
    try:
        client = get_redis()
        await client.set(key, json.dumps(data), ex=expire_seconds)
    except Exception as e:
        logger.warning(f"Redis set error: {e}")


async def invalidate_cache(key: str) -> None:
    """Delete a key from Redis to invalidate stale data."""
    try:
        client = get_redis()
        await client.delete(key)
    except Exception as e:
        logger.warning(f"Redis delete error: {e}")