# src/execution/paper_trader.py

import asyncio
import ccxt.async_support as ccxt
from utils.logger import get_logger

logger = get_logger(__name__)

class PaperTrader:
    def __init__(self, symbol: str = "BTC/USD"):
        self.symbol = symbol
        self.kraken = ccxt.kraken({'enableRateLimit': True})
        self.position = 0.0
        self.entry_price = 0.0
        self.capital = 10000.0
        self.prices: list[float] = []

    async def run(self):
        logger.info("[PaperTrader] Running moving average strategy...")
        while True:
            try:
                ticker = await self.kraken.fetch_ticker(self.symbol)
                price = ticker['last']
            except Exception as e:
                logger.error(f"[PaperTrader] price error: {e}")
                await asyncio.sleep(60)
                continue

            self.prices.append(price)
            if len(self.prices) > 20:
                self.prices.pop(0)
            short_ma = sum(self.prices[-5:]) / min(len(self.prices), 5)
            long_ma = sum(self.prices) / len(self.prices)

            if self.position == 0 and len(self.prices) >= 20:
                if short_ma > long_ma:
                    self.entry_price = price
                    self.position = self.capital * 0.1 / price
                    logger.info(
                        f"[PaperTrader] LONG {self.position:.4f} {self.symbol} at {price}"
                    )
                elif short_ma < long_ma:
                    self.entry_price = price
                    self.position = -self.capital * 0.1 / price
                    logger.info(
                        f"[PaperTrader] SHORT {abs(self.position):.4f} {self.symbol} at {price}"
                    )
            elif self.position != 0:
                change = (price - self.entry_price) / self.entry_price
                if self.position > 0 and change > 0.01 or self.position < 0 and change < -0.01:
                    pnl = (price - self.entry_price) * self.position
                    self.capital += pnl
                    logger.info(
                        f"[PaperTrader] Close position PnL {pnl:.2f} Capital {self.capital:.2f}"
                    )
                    self.position = 0

            await asyncio.sleep(60)
