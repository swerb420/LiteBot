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

    def __init__(self, tg_bot=None, redis_url: str = "redis://localhost", limit: int = 5) -> None:
        self.tg_bot = tg_bot
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
        for url in self.FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[: self.limit]:
                    headlines.append(entry.title)
            except Exception as e:  # pragma: no cover - network errors
                logger.error("[NewsAggregator] feed error: %s", e)
        data = "\n".join(headlines)
        return data

    async def alert_cached_news(self) -> None:
        if not self.tg_bot:
            return
        try:
            headlines = await self.redis.get("latest_news")
            if headlines:
                if isinstance(headlines, bytes):
                    headlines = headlines.decode()
                await self.tg_bot.send_alert(str(headlines))
        except Exception as e:  # pragma: no cover - redis errors
            logger.error("[NewsAggregator] alert error: %s", e)
