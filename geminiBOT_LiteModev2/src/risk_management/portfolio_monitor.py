# src/risk_management/portfolio_monitor.py

import asyncio
import ccxt.async_support as ccxt
from utils.logger import get_logger

logger = get_logger(__name__)

class PortfolioMonitor:
    def __init__(self):
        self.kraken = ccxt.kraken({'enableRateLimit': True})

    async def run(self):
        while True:
            logger.info("[PortfolioMonitor] Checking portfolio exposure...")
            await asyncio.sleep(300)

    async def calculate_position_size(self, symbol):
        total_capital = 10000  # Example paper capital
        risk_fraction = 0.02
        try:
            ticker = await self.kraken.fetch_ticker(symbol)
            price = ticker['last']
        except Exception as e:
            logger.warning(f"[PortfolioMonitor] Price fallback: {e}")
            price = 100
        size = (total_capital * risk_fraction) / price
        logger.info(f"[PortfolioMonitor] Size for {symbol}: {size:.4f}")
        return size
