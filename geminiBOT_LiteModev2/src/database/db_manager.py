# src/database/db_manager.py

import asyncpg
from config.settings import DATABASE_URL, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)


class DBManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                min_size=DB_POOL_MIN_SIZE,
                max_size=DB_POOL_MAX_SIZE,
            )
            logger.info("[DBManager] Pool connected.")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("[DBManager] Pool closed.")

    async def get_tracked_assets(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT symbol FROM tracked_assets WHERE is_active = TRUE;"
            )
            return [row["symbol"] for row in rows]

    async def fetch(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


# Global instance
db = DBManager()
