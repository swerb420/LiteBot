import asyncio
import feedparser
import aioredis
import aiohttp
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsAggregator:
    """Fetch and cache market-moving news from multiple RSS feeds."""

    FEEDS = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://www.reuters.com/rssFeed/marketsNews",
    ]

    def __init__(self, redis_url: str = "redis://localhost", limit: int = 5) -> None:
        self.redis = aioredis.from_url(redis_url)
        self.cache_ttl = 600
        self.limit = limit

    async def run(self) -> None:
        while True:
            await self.update_news()
            await asyncio.sleep(300)

    async def update_news(self) -> None:
        try:
            items = await self.fetch_all()
            await self.redis.set("latest_news", items, ex=self.cache_ttl)
            logger.info("[NewsAggregator] Cached %d headlines", len(items))
        except Exception as e:  # pragma: no cover - network, redis errors
            logger.error("[NewsAggregator] update error: %s", e)

    async def fetch_all(self) -> str:
        headlines = []

        async def fetch(url: str, session: aiohttp.ClientSession):
            async with session.get(url) as resp:
                text = await resp.text()
                feed = feedparser.parse(text)
                return [entry.title for entry in feed.entries[: self.limit]]

        async with aiohttp.ClientSession() as session:
            tasks = [fetch(url, session) for url in self.FEEDS]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):  # pragma: no cover - network errors
                logger.error("[NewsAggregator] feed error: %s", result)
            else:
                headlines.extend(result)

        return "\n".join(headlines)
