import os
import sys
import logging
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from signal_generation.signal_aggregator import SignalAggregator

@pytest.mark.asyncio
async def test_process_whale_signal_tallies():
    aggregator = SignalAggregator()
    await aggregator.process_whale_signal('BTC-USD', 1000, 'long')
    await aggregator.process_whale_signal('BTC-USD', 2000, 'short')
    await aggregator.process_whale_signal('ETH-USD', 500, 'long')

    assert aggregator.trade_tally == {
        'BTC-USD': {'long': 1, 'short': 1},
        'ETH-USD': {'long': 1, 'short': 0},
    }

    assert aggregator.trade_tally['ETH-USD']['short'] == 0

@pytest.mark.asyncio
async def test_log_whale_summary_resets(caplog):
    aggregator = SignalAggregator()
    await aggregator.process_whale_signal('BTC-USD', 1000, 'long')
    await aggregator.process_whale_signal('BTC-USD', 500, 'long')

    with caplog.at_level(logging.INFO):
        aggregator._log_whale_summary()

    assert any('Whale trade summary' in rec.message for rec in caplog.records)
    assert aggregator.trade_tally == {}
