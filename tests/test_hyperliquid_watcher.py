import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from onchain.hyperliquid_watcher import HyperliquidWatcher


@pytest.mark.asyncio
async def test_trades_parsed_and_forwarded(monkeypatch):
    sample_trades = [
        {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'price': '30000',
            'amount': '0.1',
            'info': {'hash': '0xabc'}
        },
        {
            'symbol': 'ETH/USD',
            'side': 'sell',
            'price': '2000',
            'amount': '1',
            'info': {'hash': '0xdef'}
        }
    ]

    decoder = SimpleNamespace(fetch_recent_trades=AsyncMock(return_value=sample_trades))
    aggregator = SimpleNamespace(process_whale_signal=AsyncMock())
    watcher = HyperliquidWatcher(decoder=decoder, signal_aggregator=aggregator, poll_interval=0)

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr('onchain.hyperliquid_watcher.asyncio.sleep', fake_sleep)

    with pytest.raises(KeyboardInterrupt):
        await watcher.run()

    aggregator.process_whale_signal.assert_any_await('BTC-USD', 3000.0, 'long')
    aggregator.process_whale_signal.assert_any_await('ETH-USD', 2000.0, 'short')
