"""
Redis Cache Service
Handles prediction caching and session management.
"""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from ..core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None

CACHE_TTL = 3600  # 1 hour
PREDICTION_PREFIX = "pred:"
SESSION_PREFIX = "session:"


async def get_redis() -> Optional[redis.Redis]:
    """Get or create Redis connection."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}. Caching disabled.")
            redis_client = None
    return redis_client


async def cache_prediction(transaction_hash: str, prediction: dict, ttl: int = CACHE_TTL):
    """Cache a prediction result."""
    client = await get_redis()
    if client:
        try:
            key = f"{PREDICTION_PREFIX}{transaction_hash}"
            await client.setex(key, ttl, json.dumps(prediction))
            logger.debug(f"Cached prediction: {key}")
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")


async def get_cached_prediction(transaction_hash: str) -> Optional[dict]:
    """Retrieve a cached prediction."""
    client = await get_redis()
    if client:
        try:
            key = f"{PREDICTION_PREFIX}{transaction_hash}"
            data = await client.get(key)
            if data:
                logger.debug(f"Cache hit: {key}")
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    return None


async def invalidate_cache(transaction_hash: str):
    """Remove a cached prediction."""
    client = await get_redis()
    if client:
        try:
            await client.delete(f"{PREDICTION_PREFIX}{transaction_hash}")
        except Exception:
            pass


async def store_session(user_id: str, token_data: dict, ttl: int = 86400):
    """Store user session data."""
    client = await get_redis()
    if client:
        try:
            key = f"{SESSION_PREFIX}{user_id}"
            await client.setex(key, ttl, json.dumps(token_data))
        except Exception as e:
            logger.warning(f"Session store failed: {e}")


async def get_session(user_id: str) -> Optional[dict]:
    """Retrieve user session data."""
    client = await get_redis()
    if client:
        try:
            key = f"{SESSION_PREFIX}{user_id}"
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
    return None


async def invalidate_session(user_id: str):
    """Remove user session."""
    client = await get_redis()
    if client:
        try:
            await client.delete(f"{SESSION_PREFIX}{user_id}")
        except Exception:
            pass
