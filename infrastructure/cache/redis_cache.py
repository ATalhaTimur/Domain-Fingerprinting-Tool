import json
import os

import redis.asyncio as redis

from core.ports.cache_port import ICache


class RedisCache(ICache):
    def __init__(self) -> None:
        self._redis = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True,
        )

    async def get(self, key: str) -> dict | None:
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else None

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        await self._redis.setex(key, ttl_seconds, json.dumps(value))
