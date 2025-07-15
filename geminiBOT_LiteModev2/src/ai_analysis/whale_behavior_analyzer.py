import numpy as np
from typing import Dict, List
from sklearn.preprocessing import StandardScaler
from database.db_manager import db
from utils.logger import get_logger

logger = get_logger(__name__)


class WhaleBehaviorAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()

    async def quick_analysis(self, wallet_address: str) -> Dict:
        try:
            query = """
                SELECT COUNT(*) as trade_count,
                       SUM(size_usd) as total_volume
                FROM wallet_trades
                WHERE wallet_address=$1 AND timestamp>NOW()-INTERVAL '30 days'
            """
            stats = await db.fetchrow(query, wallet_address)
            return {
                "trade_count": stats["trade_count"] or 0,
                "total_volume": float(stats["total_volume"] or 0),
            }
        except Exception as e:
            logger.error(f"[WhaleBehaviorAnalyzer] quick error: {e}")
            return {}

    async def deep_analysis(self, wallet_address: str) -> Dict:
        try:
            trades = await self._get_wallet_trades(wallet_address)
            performance = await self._calculate_performance_metrics(trades)
            patterns = await self._detect_trading_patterns(trades)
            return {
                "performance": performance,
                "patterns": patterns,
            }
        except Exception as e:
            logger.error(f"[WhaleBehaviorAnalyzer] deep error: {e}")
            return {"performance": {}, "patterns": []}

    async def comprehensive_ai_analysis(self, wallet_address: str) -> Dict:
        trades = await self._get_wallet_trades(wallet_address, days=90)
        if len(trades) < 10:
            return {"error": "Insufficient trading history for AI analysis"}
        features = await self._extract_ml_features(trades)
        behavior = await self._classify_behavior(features)
        return {"behavior": behavior}

    async def start_tracking(self, wallet_address: str):
        logger.info(f"[WhaleBehaviorAnalyzer] tracking {wallet_address}")

    async def _get_wallet_trades(
        self, wallet_address: str, days: int = 30
    ) -> List[Dict]:
        query = """
            SELECT *, EXTRACT(EPOCH FROM timestamp) as ts
            FROM wallet_trades
            WHERE wallet_address=$1
              AND timestamp > NOW() - $2 * INTERVAL '1 day'
            ORDER BY timestamp
        """
        rows = await db.fetch(query, wallet_address, days)
        return [dict(r) for r in rows]

    async def _calculate_performance_metrics(self, trades: List[Dict]) -> Dict:
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        total_trades = len(trades)
        win_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
        win_rate = win_trades / total_trades * 100 if total_trades else 0
        return {
            "total_pnl": total_pnl,
            "total_trades": total_trades,
            "win_rate": win_rate,
        }

    async def _detect_trading_patterns(self, trades: List[Dict]) -> List[Dict]:
        patterns = []
        if not trades:
            return patterns
        directions = [t["direction"] for t in trades if t.get("direction")]
        if directions.count("long") / len(directions) > 0.8:
            patterns.append({"name": "Perma-Bull", "confidence": 0.9})
        return patterns

    async def _extract_ml_features(self, trades: List[Dict]) -> np.ndarray:
        sizes = [t["size_usd"] for t in trades if t.get("size_usd")]
        returns = [t.get("pnl", 0) for t in trades]
        features = np.array(
            [
                np.mean(sizes) if sizes else 0,
                np.std(sizes) if sizes else 0,
                np.mean(returns) if returns else 0,
            ]
        )
        return features

    async def _classify_behavior(self, features: np.ndarray) -> Dict:
        avg_size = features[0]
        if avg_size > 500000:
            strategy = "institutional"
        else:
            strategy = "retail"
        return {"primary_strategy": strategy}
