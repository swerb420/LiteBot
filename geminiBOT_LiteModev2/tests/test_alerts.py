import sys
from pathlib import Path
from types import SimpleNamespace
import asyncio
import pytest

# add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def patch_heavy_modules(monkeypatch):
    modules = {
        "execution.telegram_wallet_manager": SimpleNamespace(WalletManager=object),
        "ai_analysis.whale_behavior_analyzer": SimpleNamespace(),
        "execution.telegram_bot": SimpleNamespace(TelegramBot=object),
        "signal_generation.signal_aggregator": SimpleNamespace(SignalAggregator=object),
    }
    for name, stub in modules.items():
        monkeypatch.setitem(sys.modules, name, stub)
    yield

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
async def test_tracked_wallet_alert(monkeypatch, patch_heavy_modules):
    from onchain.enhanced_whale_watcher import EnhancedWhaleWatcher
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


@pytest.mark.asyncio
async def test_alert_respects_settings(monkeypatch, patch_heavy_modules):
    from onchain.enhanced_whale_watcher import EnhancedWhaleWatcher
    tg = DummyTG()
    monkeypatch.setattr(
        "onchain.whale_watcher.WhaleWatcher.__init__",
        lambda self, tg_bot: setattr(self, "tg_bot", tg_bot),
    )
    watcher = EnhancedWhaleWatcher(tg)
    monkeypatch.setattr("onchain.enhanced_whale_watcher.db", dummy_db)
    watcher.wallet_alerts["0xabc"] = {
        "direction": "long",
        "interval": 10,
        "last_sent": -100,
        "min_size": 10000,
    }
    class FakeLoop:
        def __init__(self):
            self.t = 0
        def time(self):
            return self.t

    loop = FakeLoop()
    monkeypatch.setattr(asyncio, "get_event_loop", lambda: loop)
    trade_data = {"direction": "long", "size_usd": 15000}
    await watcher._send_tracked_wallet_alert("0xabc", trade_data, "GMX")
    assert tg.messages == ["Tracked Wallet Test long $15,000 on GMX"]
    loop.t = 5
    await watcher._send_tracked_wallet_alert("0xabc", trade_data, "GMX")
    assert len(tg.messages) == 1  # interval not passed
    loop.t = 15
    await watcher._send_tracked_wallet_alert("0xabc", trade_data, "GMX")
    assert len(tg.messages) == 2

# Remove stub modules so other tests can import the real implementations
for name in (
    "execution.telegram_wallet_manager",
    "ai_analysis.whale_behavior_analyzer",
    "execution.telegram_bot",
    "signal_generation.signal_aggregator",
):
    sys.modules.pop(name, None)
