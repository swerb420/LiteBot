# src/ai_analysis/sentiment_mobilebert.py

import asyncio
from transformers import pipeline
from utils.logger import get_logger
from config.settings import ENABLE_MOBILEBERT, BERT_MODEL_NAME

logger = get_logger(__name__)

class SentimentAnalyzer:
    """
    Async MobileBERT sentiment analyzer.
    Uses CPU only.
    """

    def __init__(self):
        self.pipeline = None
        self._loaded = False

    async def _load(self):
        if self._loaded:
            return
        if not ENABLE_MOBILEBERT:
            logger.warning("[SentimentAnalyzer] MobileBERT disabled via config")
            self.pipeline = lambda text: [{"label": "NEUTRAL", "score": 0.0}]
            self._loaded = True
            return
        logger.info("[SentimentAnalyzer] Loading MobileBERT...")
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=BERT_MODEL_NAME,
            device=-1,
        )
        self._loaded = True
        logger.info("[SentimentAnalyzer] MobileBERT model loaded.")

    async def run(self):
        await self._load()
        while True:
            await asyncio.sleep(3600)

    async def analyze(self, text: str) -> dict:
        if not self._loaded:
            await self._load()
        try:
            result = self.pipeline(text[:512])[0]
            logger.debug(f"[SentimentAnalyzer] {result}")
            return result
        except Exception as e:
            logger.error(f"[SentimentAnalyzer] Error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
