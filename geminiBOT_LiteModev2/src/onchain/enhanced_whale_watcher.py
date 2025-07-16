import asyncio
from web3 import Web3
from typing import Dict

from utils.logger import get_logger
from database.db_manager import db
from onchain.whale_watcher import WhaleWatcher
from execution.telegram_bot import TelegramBot

logger = get_logger(__name__)


class EnhancedWhaleWatcher(WhaleWatcher):
    def __init__(self, tg_bot: TelegramBot):
        super().__init__(tg_bot)
        self.tracked_wallets = set()
        self.wallet_alerts = {}

    async def run(self):
        logger.info("[EnhancedWhaleWatcher] Starting enhanced whale tracker...")
        await self._load_tracked_wallets()
        await super().run()

    async def _load_tracked_wallets(self):
        query = """
            SELECT wallet_address, min_trade_size,
                   alert_direction, alert_interval, metadata
            FROM tracked_wallets WHERE tracking_enabled=true
        """
        wallets = await db.fetch(query)
        for w in wallets:
            self.tracked_wallets.add(w['wallet_address'].lower())
            self.wallet_alerts[w['wallet_address'].lower()] = {
                'min_size': w['min_trade_size'],
                'direction': w.get('alert_direction', 'both'),
                'interval': w.get('alert_interval', 0),
                'settings': w.get('metadata', {}),
                'last_sent': 0,
            }
        logger.info(f"[EnhancedWhaleWatcher] Loaded {len(self.tracked_wallets)} wallets")

    async def _process_log(self, log: Dict, protocol: str):
        try:
            wallet = Web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
            is_tracked = wallet.lower() in self.tracked_wallets
            await super()._process_log(log, protocol)
            if is_tracked:
                await self._process_tracked_wallet_activity(wallet, log, protocol)
        except Exception as e:
            logger.error(f"[EnhancedWhaleWatcher] processing error: {e}")

    async def _decode_trade_details(self, log: Dict, protocol: str) -> Dict:
        """Decode trade details for a given protocol."""
        if protocol.lower() == "gmx":
            return self.decode_increase_position(log)
        return {}

    async def _process_tracked_wallet_activity(self, wallet: str, log: Dict, protocol: str):
        try:
            await db.execute("UPDATE tracked_wallets SET last_activity=NOW() WHERE wallet_address=$1", wallet)
            trade_data = await self._decode_trade_details(log, protocol)
            alert_settings = self.wallet_alerts.get(wallet.lower(), {})
            min_size = alert_settings.get('min_size', 10000)
            if trade_data['size_usd'] >= min_size:
                await self._send_tracked_wallet_alert(wallet, trade_data, protocol)
        except Exception as e:
            logger.error(f"[EnhancedWhaleWatcher] tracked wallet error: {e}")

    async def _send_tracked_wallet_alert(self, wallet: str, trade_data: Dict, protocol: str):
        settings = self.wallet_alerts.get(wallet.lower(), {})
        direction_pref = settings.get('direction', 'both')
        interval = settings.get('interval', 0)
        last_sent = settings.get('last_sent', 0)
        if direction_pref != 'both' and trade_data['direction'] != direction_pref:
            return
        now = asyncio.get_event_loop().time()
        if interval and now - last_sent < interval:
            return
        wallet_info = await db.fetchrow(
            "SELECT label, category FROM tracked_wallets WHERE wallet_address=$1",
            wallet,
        )
        label = wallet_info['label'] if wallet_info else 'Unknown'
        message = (
            f"Tracked Wallet {label} {trade_data['direction']} ${trade_data['size_usd']:,.0f} on {protocol}"
        )
        settings['last_sent'] = now
        self.wallet_alerts[wallet.lower()] = settings
        await self.tg_bot.send_alert(message)
