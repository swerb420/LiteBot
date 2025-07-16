# === 4️⃣ src/onchain/hyperliquid_decoder.py ===
# ➜ Location: src/onchain/hyperliquid_decoder.py
from hyperliquid import HyperliquidAsync
from utils.logger import get_logger

logger = get_logger(__name__)

class HyperliquidDecoder:
    def __init__(self):
        self.api = HyperliquidAsync()

    async def fetch_recent_trades(self, symbol: str = "BTCUSD", limit: int = 50):
        try:
            data = await self.api.fetch_trades(symbol, limit=limit)
            logger.info(f"[HyperliquidDecoder] Recent trades: {len(data)}")
            return data
        except Exception as e:
            logger.error(f"[HyperliquidDecoder] fetch error: {e}")
            return []

