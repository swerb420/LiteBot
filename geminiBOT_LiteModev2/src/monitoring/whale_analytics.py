from typing import Dict, List
from datetime import datetime
from database.db_manager import db
from utils.logger import get_logger
from utils.cache import cache

logger = get_logger(__name__)


class WhaleAnalytics:
    async def generate_daily_report(self) -> Dict:
        try:
            top_whales = await self._get_top_whales("daily")
            sentiment = await self._calculate_whale_sentiment()
            report = {
                "date": datetime.utcnow().date(),
                "top_performers": top_whales,
                "market_sentiment": sentiment,
            }
            await cache.set("daily_whale_report", report, ttl=86400)
            return report
        except Exception as e:
            logger.error(f"[WhaleAnalytics] report error: {e}")
            return {}

    async def _get_top_whales(self, period: str, limit: int = 10) -> List[Dict]:
        rows = await db.fetch(
            """
            SELECT tw.wallet_address, tw.label, wp.total_pnl
            FROM tracked_wallets tw JOIN wallet_performance wp
            ON tw.wallet_address=wp.wallet_address
            WHERE wp.period=$1 ORDER BY wp.total_pnl DESC LIMIT $2
            """,
            period,
            limit,
        )
        return [dict(r) for r in rows]

    async def _calculate_whale_sentiment(self) -> Dict:
        result = await db.fetchrow(
            """
            SELECT SUM(CASE WHEN direction='long' THEN size_usd ELSE 0 END) as long_volume,
                   SUM(CASE WHEN direction='short' THEN size_usd ELSE 0 END) as short_volume
            FROM wallet_trades WHERE timestamp>NOW()-INTERVAL '24 hours'
            """
        )
        if not result:
            return {"sentiment": "neutral"}
        total = (result["long_volume"] or 0) + (result["short_volume"] or 0)
        long_ratio = result["long_volume"] / total if total else 0.5
        sentiment = (
            "bullish"
            if long_ratio > 0.65
            else "bearish" if long_ratio < 0.35 else "neutral"
        )
        return {"sentiment": sentiment, "long_ratio": long_ratio}


whale_analytics = WhaleAnalytics()
