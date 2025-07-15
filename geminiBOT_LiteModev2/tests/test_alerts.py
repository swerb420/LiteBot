import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

# add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Stub heavy modules before import
sys.modules.setdefault("execution.telegram_wallet_manager", SimpleNamespace(WalletManager=object))
sys.modules.setdefault("ai_analysis.whale_behavior_analyzer", SimpleNamespace())
sys.modules.setdefault("execution.telegram_bot", SimpleNamespace(TelegramBot=object))
sys.modules.setdefault("signal_generation.signal_aggregator", SimpleNamespace(SignalAggregator=object))

from onchain.enhanced_whale_watcher import EnhancedWhaleWatcher

class DummyDB:
    async def fetchrow(self, query, wallet):
        return {"label": "Test"}

dummy_db = DummyDB()

class DummyTG:
    def __init__(self):
        self.messages = []
    async def send_alert(self, message: str):
        self.messages.append(message)

@pytest.mark.asyncio
async def test_tracked_wallet_alert(monkeypatch):
    tg = DummyTG()
    monkeypatch.setattr(
        "onchain.whale_watcher.WhaleWatcher.__init__",
        lambda self, tg_bot: setattr(self, "tg_bot", tg_bot)
    )
    watcher = EnhancedWhaleWatcher(tg)
    monkeypatch.setattr("onchain.enhanced_whale_watcher.db", dummy_db)
    trade_data = {"direction": "long", "size_usd": 15000}
    await watcher._send_tracked_wallet_alert("0xabc", trade_data, "GMX")
    assert tg.messages == ["Tracked Wallet Test long $15,000 on GMX"]
