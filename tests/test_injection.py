import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pytest

import sys
sys.path.insert(0, 'geminiBOT_LiteModev2/src')

from ai_analysis.whale_behavior_analyzer import WhaleBehaviorAnalyzer
from execution.telegram_wallet_manager import WalletManager

class DummyBot:
    def __init__(self):
        self.application = SimpleNamespace(add_handler=lambda *a, **k: None)


async def dummy_reply(*args, **kwargs):
    pass

class DummyMessage:
    def __init__(self, text=''):
        self.text = text
    async def reply_text(self, *args, **kwargs):
        await dummy_reply()

class DummyUpdate:
    def __init__(self, text=''):
        self.message = DummyMessage(text)

@pytest.mark.asyncio
async def test_get_wallet_trades_injection():
    analyzer = WhaleBehaviorAnalyzer()
    malicious_days = "30; DROP TABLE x;"
    with patch('ai_analysis.whale_behavior_analyzer.db.fetch', new=AsyncMock(return_value=[])) as mock_fetch:
        await analyzer._get_wallet_trades('0xabc', malicious_days)
        assert mock_fetch.await_count == 1
        called_query = mock_fetch.call_args.args[0]
        assert 'DROP' not in called_query
        assert "($2 || ' days')::interval" in called_query

@pytest.mark.asyncio
async def test_edit_wallet_value_invalid_field():
    manager = WalletManager(DummyBot())
    update = DummyUpdate('new')
    context = SimpleNamespace(user_data={'edit_field': 'label; DROP TABLE', 'edit_wallet': '0xabc'})
    with patch('execution.telegram_wallet_manager.db.execute', new=AsyncMock()) as mock_exec:
        await manager.edit_wallet_value(update, context)
        mock_exec.assert_not_awaited()
