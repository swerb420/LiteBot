# src/ai_analysis/sentiment_mobilebert.py

import asyncio
from transformers import pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer:
    """
    Async MobileBERT sentiment analyzer.
    Uses CPU only.
    """

    def __init__(self):
        self.pipeline = None

    async def run(self):
        logger.info("[SentimentAnalyzer] Loading MobileBERT...")
        self.pipeline = pipeline(
            "sentiment-analysis",
            model="textattack/mobilebert-uncased-SST-2",
            device=-1
        )
        logger.info("[SentimentAnalyzer] MobileBERT model loaded.")
        while True:
            await asyncio.sleep(3600)

    def analyze(self, text: str) -> dict:
        if not self.pipeline:
            return {"label": "NEUTRAL", "score": 0.5}
        try:
            result = self.pipeline(text[:512])[0]
            logger.debug(f"[SentimentAnalyzer] {result}")
            return result
        except Exception as e:
            logger.error(f"[SentimentAnalyzer] Error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
