# src/execution/paper_trader.py

import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

class PaperTrader:
    def __init__(self):
        self.open_trades = []

    async def run(self):
        logger.info("[PaperTrader] Running in paper mode...")
        while True:
            # Example dummy trade
            logger.info("[PaperTrader] Would execute trade...")
            await asyncio.sleep(60)
