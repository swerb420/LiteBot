import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from onchain import whale_watcher as ww

@pytest.mark.asyncio
async def test_handle_log_invokes_process(monkeypatch):
    monkeypatch.setattr(ww.WhaleWatcher, '__init__', lambda self, tg_bot=None: None)
    watcher = ww.WhaleWatcher(None)
    process = AsyncMock()
    watcher._process_log = process
    log = {'foo': 'bar'}
    await watcher.handle_log(log)
    process.assert_awaited_once_with(log, 'GMX')

@pytest.mark.asyncio
async def test_handle_log_logs_errors(monkeypatch):
    monkeypatch.setattr(ww.WhaleWatcher, '__init__', lambda self, tg_bot=None: None)
    watcher = ww.WhaleWatcher(None)
    err = Exception('boom')
    watcher._process_log = AsyncMock(side_effect=err)
    logged = []
    monkeypatch.setattr(ww, 'logger', SimpleNamespace(error=lambda msg: logged.append(msg)))
    await watcher.handle_log({})
    assert logged == [f"[WhaleWatcher] handle_log error: {err}"]


@pytest.mark.asyncio
async def test_write_trade_uses_db_execute(monkeypatch):
    monkeypatch.setattr(ww.WhaleWatcher, '__init__', lambda self, tg_bot=None: None)
    watcher = ww.WhaleWatcher(None)
    exec_mock = AsyncMock()
    watcher.db = SimpleNamespace(execute=exec_mock)
    monkeypatch.setattr(ww, 'metrics', SimpleNamespace(inc=lambda *a, **k: None))
    monkeypatch.setattr(
        ww,
        'logger',
        SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None),
    )

    data = {
        'symbol': 'BTC-USD',
        'size_usd': 100,
        'leverage': 2,
        'direction': 'long',
        'tx_hash': '0xabc',
    }

    await watcher.write_trade('0xwallet', 'GMX', 'open', data)

    exec_mock.assert_awaited_once()
