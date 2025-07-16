# === 5️⃣ src/main.py ===
# ➜ Location: src/main.py
import asyncio
from config.settings import setup_logging, ENABLE_METRICS_SERVER, METRICS_PORT
from utils.logger import get_logger
from database.db_manager import DBManager
from execution.telegram_bot import TelegramBot
from ai_analysis.ensemble_manager import EnsembleManager
from signal_generation.signal_aggregator import SignalAggregator
from risk_management.portfolio_monitor import PortfolioMonitor
from monitoring.system_monitor import SystemMonitor
from monitoring.api_monitor import ApiMonitor
from monitoring.metrics_server import MetricsServer
from execution.paper_trader import PaperTrader
from async_task_supervisor import run_with_retry
from onchain.enhanced_whale_watcher import EnhancedWhaleWatcher
from onchain.hyperliquid_watcher import HyperliquidWatcher
from monitoring.whale_analytics import whale_analytics

setup_logging()
logger = get_logger(__name__)

class TradingSystem:
    def __init__(self):
        self.components = []
        self.db_manager = DBManager()

    async def initialize_components(self):
        await self.db_manager.connect()
        symbols = await self.db_manager.get_tracked_assets()
        await self.db_manager.disconnect()

        self.trade_executor = PaperTrader()
        telegram_bot = TelegramBot()

        self.components = [
            telegram_bot,
            EnsembleManager(),
            SignalAggregator(),
            PortfolioMonitor(),
            SystemMonitor(),
            ApiMonitor(),
            self.trade_executor,
            EnhancedWhaleWatcher(telegram_bot),
            HyperliquidWatcher()
        ]
        if ENABLE_METRICS_SERVER:
            self.components.append(MetricsServer(METRICS_PORT))

    async def run(self):
        logger.info("[System] Starting Trading Bot in Lite Mode with Whale Tracker")
        await self.initialize_components()
        try:
            async with asyncio.TaskGroup() as tg:
                for component in self.components:
                    if hasattr(component, 'run'):
                        tg.create_task(run_with_retry(component.run))
        except (KeyboardInterrupt, SystemExit):
            logger.info("[System] Shutdown initiated.")
        finally:
            await self.shutdown()

    async def shutdown(self):
        logger.info("[System] Graceful shutdown complete.")

if __name__ == "__main__":
    system = TradingSystem()
    asyncio.run(system.run())

# ✅ Put each file exactly as listed, match the paths, no placeholders.
# ✅ Then run your Whale Tracker on your VPS with docker-compose up --build
