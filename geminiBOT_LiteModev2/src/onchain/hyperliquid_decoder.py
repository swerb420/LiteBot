# === 4️⃣ src/onchain/hyperliquid_decoder.py ===
# ➜ Location: src/onchain/hyperliquid_decoder.py
from hyperliquid import HyperliquidAPI
from utils.logger import get_logger

logger = get_logger(__name__)


class HyperliquidDecoder:
    def __init__(self):
        self.api = HyperliquidAPI()

    async def fetch_recent_trades(self):
        try:
            data = await self.api.get_recent_trades()
            logger.info(f"[HyperliquidDecoder] Recent trades: {data}")
            return data
        except Exception as e:
            logger.error(f"[HyperliquidDecoder] fetch error: {e}")
            return []
