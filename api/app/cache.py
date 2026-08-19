import json
import logging
from typing import Any

import redis

from app.config import get_settings

logger = logging.getLogger("app.cache")

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Return a shared Redis client, creating it on first use."""
    global _client
    if _client is None:
        _client = redis.from_url(get_settings().redis_url, decode_responses=True)
    return _client


def cache_get_json(client: redis.Redis, key: str) -> Any | None:
    raw = client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


def cache_set_json(client: redis.Redis, key: str, value: Any, ttl_seconds: int) -> None:
    """Store value as JSON with a mandatory TTL.

    IMPORTANT: ttl_seconds has no default. Every cache entry in this app must
    expire — a forgotten TTL is how a cache silently starts lying forever.
    """
    client.set(key, json.dumps(value, default=str), ex=ttl_seconds)


def cache_delete(client: redis.Redis, key: str) -> None:
    client.delete(key)
