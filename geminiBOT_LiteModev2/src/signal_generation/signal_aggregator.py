# src/signal_generation/signal_aggregator.py

import asyncio
from utils.logger import get_logger
from ai_analysis.sentiment_mobilebert import SentimentAnalyzer

logger = get_logger(__name__)


class SignalAggregator:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    async def run(self):
        asyncio.create_task(self.sentiment_analyzer.run())
        while True:
            signals = [
                {"symbol": "AAPL", "text": "Apple beats earnings estimates."},
                {"symbol": "BTC-USD", "text": "Bitcoin hits new local high."},
            ]
            combined = []
            for sig in signals:
                sentiment = await self.sentiment_analyzer.analyze(sig["text"])
                sig["sentiment"] = sentiment
                combined.append(sig)
            logger.info(f"[SignalAggregator] Signals: {combined}")
            await asyncio.sleep(60)

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
            # TODO: aggregate whale activity with other market signals
        except Exception as e:
            logger.error(f"[SignalAggregator] process_whale_signal error: {e}")
