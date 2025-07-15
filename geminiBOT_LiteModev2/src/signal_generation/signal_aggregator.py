# src/signal_generation/signal_aggregator.py

import asyncio
from utils.logger import get_logger
from ai_analysis.sentiment_mobilebert import SentimentAnalyzer

logger = get_logger(__name__)


class SignalAggregator:
    def __init__(self, summary_interval: int = 300):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trade_tally: dict[str, dict[str, int]] = {}
        self._summary_interval = summary_interval

    async def run(self):
        asyncio.create_task(self.sentiment_analyzer.run())
        asyncio.create_task(self._whale_summary_loop())
        while True:
            signals = [
                {"symbol": "AAPL", "text": "Apple beats earnings estimates."},
                {"symbol": "BTC-USD", "text": "Bitcoin hits new local high."}
            ]
            combined = []
            for sig in signals:
                sentiment = await self.sentiment_analyzer.analyze(sig['text'])
                sig['sentiment'] = sentiment
                combined.append(sig)
            logger.info(f"[SignalAggregator] Signals: {combined}")
            await asyncio.sleep(60)

    async def _whale_summary_loop(self):
        while True:
            await asyncio.sleep(self._summary_interval)
            self._log_whale_summary()

    def _log_whale_summary(self):
        if not self.trade_tally:
            return
        parts = []
        for symbol, dirs in self.trade_tally.items():
            segs = [f"{d} x{c}" for d, c in dirs.items() if c]
            if segs:
                parts.append(f"{symbol} {' '.join(segs)}")
        if parts:
            summary = " | ".join(parts)
            logger.info(f"[SignalAggregator] Whale trade summary: {summary}")
        self.trade_tally.clear()

    async def process_whale_signal(self, symbol: str, size_usd: float, direction: str):
        """Process large whale trade events.

        This placeholder simply logs the received trade details so that
        :class:`~onchain.whale_watcher.WhaleWatcher` can pass data here
        without raising errors. More complex aggregation logic can be
        implemented later.
        """
        try:
            logger.info(
                f"[SignalAggregator] Whale trade {symbol} {direction} "
                f"${size_usd:,.2f}"
            )
            tally = self.trade_tally.setdefault(symbol, {"long": 0, "short": 0})
            if direction not in tally:
                tally[direction] = 0
            tally[direction] += 1
        except Exception as e:
            logger.error(f"[SignalAggregator] process_whale_signal error: {e}")
