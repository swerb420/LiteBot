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
async def test_run_exits_when_ws_url_missing(monkeypatch):
    monkeypatch.setenv('ALCHEMY_WS_URL', '')
    monkeypatch.setenv('GMX_VAULT_ADDRESS', '0x' + '1'*40)
    import importlib
    import onchain.whale_watcher as ww_reload
    importlib.reload(ww_reload)

    connect_mock = AsyncMock()
    monkeypatch.setattr(ww_reload.DBManager, 'connect', connect_mock)

    watcher = ww_reload.WhaleWatcher(None)
    assert watcher.enabled is False

    await watcher.run()

    connect_mock.assert_not_awaited()
