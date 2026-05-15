import json
import time

import aiosqlite

from core.ports.cache_port import ICache

_DB_PATH = "cache/scans.db"
_INIT_SQL = """
CREATE TABLE IF NOT EXISTS scans (
    domain     TEXT PRIMARY KEY,
    data       TEXT NOT NULL,
    expires_at REAL NOT NULL
)
"""


class SqliteCache(ICache):
    async def _ensure_table(self, db: aiosqlite.Connection) -> None:
        await db.execute(_INIT_SQL)
        await db.commit()

    async def get(self, key: str) -> dict | None:
        async with aiosqlite.connect(_DB_PATH) as db:
            await self._ensure_table(db)
            async with db.execute(
                "SELECT data FROM scans WHERE domain = ? AND expires_at > ?",
                (key, time.time()),
            ) as cursor:
                row = await cursor.fetchone()
        return json.loads(row[0]) if row else None

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        async with aiosqlite.connect(_DB_PATH) as db:
            await self._ensure_table(db)
            await db.execute(
                "INSERT OR REPLACE INTO scans (domain, data, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time() + ttl_seconds),
            )
            await db.commit()
