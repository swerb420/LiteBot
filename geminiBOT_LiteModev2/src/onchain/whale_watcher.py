
# === 1️⃣ WhaleWatcher with WebSocket ===
import asyncio
import os
from web3 import AsyncWeb3, Web3
from web3.providers.persistent.websocket import WebSocketProvider as AsyncWebsocketProvider
from utils.logger import get_logger
from utils.metrics import metrics
from database.db_manager import DBManager
from execution.telegram_bot import TelegramBot
from signal_generation.signal_aggregator import SignalAggregator

logger = get_logger(__name__)

ALCHEMY_WS_URL = os.getenv("ALCHEMY_WS_URL", "")
_vault_addr = os.getenv("GMX_VAULT_ADDRESS")
if _vault_addr:
    GMX_VAULT = Web3.to_checksum_address(_vault_addr)
else:
    GMX_VAULT = None
    logger.warning("[WhaleWatcher] GMX_VAULT_ADDRESS not set")
SIG_POSITION_OPEN = Web3.keccak(text="IncreasePosition(address,address,address,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256)").hex()
SIG_POSITION_CLOSE = Web3.keccak(text="DecreasePosition(...)").hex()

class WhaleWatcher:
    def __init__(self, tg_bot: TelegramBot):
        if not ALCHEMY_WS_URL:
            logger.error("[WhaleWatcher] ALCHEMY_WS_URL not set - disabling watcher")
            self.enabled = False
            self.w3 = None
        else:
            self.w3 = AsyncWeb3(AsyncWebsocketProvider(ALCHEMY_WS_URL))
            self.enabled = True
        self.db = DBManager()
        self.tg_bot = tg_bot
        self.signal_aggregator = SignalAggregator()

    async def run(self):
        if not getattr(self, 'enabled', True):
            logger.warning("[WhaleWatcher] disabled - skipping run")
            return
        if GMX_VAULT is None:
            logger.warning(
                "[WhaleWatcher] GMX_VAULT_ADDRESS unset - disabling GMX monitoring"
            )
            return
        await self.db.connect()
        event_filter = await self.w3.eth.filter({"address": GMX_VAULT})
        logger.info("[WhaleWatcher] WebSocket listening...")
        while True:
            try:
                logs = await event_filter.get_new_entries()
                for log in logs:
                    await self.handle_log(log)
            except Exception as e:
                logger.error(f"[WhaleWatcher] WS error: {e}")
            await asyncio.sleep(1)

    async def handle_log(self, log):
        try:
            await self._process_log(log, "GMX")
        except Exception as e:
            logger.error(f"[WhaleWatcher] handle_log error: {e}")

    async def _process_log(self, log, protocol: str):
        sig = log["topics"][0].hex()
        wallet = Web3.to_checksum_address('0x' + log["topics"][1].hex()[-40:])
        metrics.inc("logs_processed")
        if sig == SIG_POSITION_OPEN:
            data = self.decode_increase_position(log)
            await self.write_trade(wallet, protocol, "open", data)
            metrics.inc("trades_opened")
            await self.tg_bot.send_alert(
                f"🐋 Whale {wallet} opened {data['size_usd']:.2f}$ {data['direction']}"
            )
            await self.signal_aggregator.process_whale_signal(
                data['symbol'], data['size_usd'], data['direction']
            )
        elif sig == SIG_POSITION_CLOSE:
            await self.link_pnl(wallet, log)
            metrics.inc("trades_closed")

    def decode_increase_position(self, log):
        data = log["data"]
        size_usd = int(data[2:66], 16) / 1e30
        leverage = int(data[66:130], 16) / 1e30
        direction = "long"
        return {
            "symbol": "BTC-USD",
            "size_usd": size_usd,
            "leverage": leverage,
            "direction": direction,
            "tx_hash": log["transactionHash"].hex()
        }

    def decode_decrease_position(self, log):
        data = log["data"]
        size_usd = int(data[2:66], 16) / 1e30
        pnl = int(data[130:194], 16) / 1e30
        return {
            "pnl": pnl,
            "size_usd": size_usd,
            "tx_hash": log["transactionHash"].hex()
        }

    async def write_trade(self, wallet, protocol, action, data):
        try:
            await self.db.pool.execute(
                """
                INSERT INTO wallet_trades(wallet_address, protocol, action, symbol, size_usd, leverage, direction, tx_hash)
                VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING
                """,
                wallet, protocol, action,
                data["symbol"], data["size_usd"], data["leverage"], data["direction"], data["tx_hash"]
            )
            metrics.inc("trades_recorded")
            logger.info(f"[WhaleWatcher] {protocol} {action} {data}")
        except Exception as e:
            logger.error(f"[WhaleWatcher] write_trade error: {e}")

    async def link_pnl(self, wallet, log):
        data = self.decode_decrease_position(log)
        logger.info(f"[WhaleWatcher] Linking PnL for {wallet} -> {data['pnl']}")
        row = await self.db.fetchrow(
            "SELECT id FROM wallet_trades WHERE wallet_address=$1 AND action='open' ORDER BY timestamp DESC LIMIT 1",
            wallet,
        )
        if row:
            await self.db.execute(
                "UPDATE wallet_trades SET pnl=$1, action='close' WHERE id=$2",
                data["pnl"], row["id"],
            )

