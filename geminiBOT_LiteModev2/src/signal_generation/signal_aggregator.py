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
                {"symbol": "BTC-USD", "text": "Bitcoin hits new local high."}
            ]
            combined = []
            for sig in signals:
                sentiment = await self.sentiment_analyzer.analyze(sig['text'])
                sig['sentiment'] = sentiment
                combined.append(sig)
            logger.info(f"[SignalAggregator] Signals: {combined}")
            await asyncio.sleep(60)
