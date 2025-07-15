import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from risk_management import portfolio_monitor as pm

@pytest.mark.asyncio
async def test_calculate_position_size(monkeypatch):
    monkeypatch.setattr(pm.PortfolioMonitor, '__init__', lambda self: setattr(self, 'kraken', SimpleNamespace(fetch_ticker=AsyncMock(return_value={'last': 50}))))
    monitor = pm.PortfolioMonitor()
    size = await monitor.calculate_position_size('BTC/USD')
    assert size == 4

@pytest.mark.asyncio
async def test_calculate_position_size_fallback(monkeypatch):
    monkeypatch.setattr(pm.PortfolioMonitor, '__init__', lambda self: setattr(self, 'kraken', SimpleNamespace(fetch_ticker=AsyncMock(side_effect=RuntimeError('fail')))))
    logged = []
    monkeypatch.setattr(pm, 'logger', SimpleNamespace(info=lambda *a, **k: None, warning=lambda msg: logged.append(msg)))
    monitor = pm.PortfolioMonitor()
    size = await monitor.calculate_position_size('ETH/USD')
    assert size == 2
    assert logged and 'fail' in logged[0]
