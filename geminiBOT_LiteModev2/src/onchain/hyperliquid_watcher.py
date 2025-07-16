import asyncio
from typing import List, Dict, Any

from utils.logger import get_logger
from signal_generation.signal_aggregator import SignalAggregator
from onchain.hyperliquid_decoder import HyperliquidDecoder

logger = get_logger(__name__)


class HyperliquidWatcher:
    """Periodically poll Hyperliquid for recent trades and forward them."""

    def __init__(
        self,
        decoder: HyperliquidDecoder | None = None,
        signal_aggregator: SignalAggregator | None = None,
        poll_interval: float = 30.0,
    ) -> None:
        self.decoder = decoder or HyperliquidDecoder()
        self.signal_aggregator = signal_aggregator or SignalAggregator()
        self.poll_interval = poll_interval

    async def run(self) -> None:
        logger.info("[HyperliquidWatcher] Starting watcher...")
        while True:
            trades = await self.decoder.fetch_recent_trades()
            await self._process_trades(trades)
            await asyncio.sleep(self.poll_interval)

    async def _process_trades(self, trades: List[Dict[str, Any]]) -> None:
        for trade in trades:
            data = self._convert_trade(trade)
            if not data:
                continue
            await self.signal_aggregator.process_whale_signal(
                data["symbol"], data["size_usd"], data["direction"]
            )

    def _convert_trade(self, trade: Dict[str, Any]) -> Dict[str, Any] | None:
        try:
            price = float(trade.get("price", 0))
            amount = float(trade.get("amount", 0))
            side = trade.get("side", "")
            symbol = trade.get("symbol", "").replace("/", "-")
            direction = "long" if side == "buy" else "short"
            return {
                "symbol": symbol,
                "size_usd": price * amount,
                "leverage": 1.0,
                "direction": direction,
                "tx_hash": trade.get("info", {}).get("hash", ""),
            }
        except Exception as e:  # pragma: no cover - defensive
            logger.error(f"[HyperliquidWatcher] trade parse error: {e}")
            return None
