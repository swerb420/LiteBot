# src/data_ingestion/reddit_scraper.py

import asyncio
import aioredis
from utils.logger import get_logger

logger = get_logger(__name__)


class RedditScraper:
    def __init__(self, redis_url="redis://localhost"):
        self.redis = aioredis.from_url(redis_url)
        self.cache_ttl = 600  # 10 minutes

    async def run(self):
        while True:
            cached = await self.redis.get("reddit_feed")
            if cached:
                logger.info("[RedditScraper] Using cached data")
            else:
                logger.info("[RedditScraper] Fetching fresh Reddit data")
                data = await self.fetch_data()
                await self.redis.set("reddit_feed", data, ex=self.cache_ttl)
            await asyncio.sleep(60)

    async def fetch_data(self):
        return "Simulated Reddit data..."
