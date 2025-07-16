import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from execution.telegram_wallet_manager import WalletManager, FIELD_MAP
from database import db_manager as db_module


class DummyBot:
    def __init__(self):
        self.application = SimpleNamespace(add_handler=lambda *a, **k: None)


class DummyMessage:
    def __init__(self, text=""):
        self.text = text
        self.replies = []

    async def reply_text(self, text, **kwargs):
        self.replies.append((text, kwargs))


class DummyUpdate:
    def __init__(self, text=""):
        self.message = DummyMessage(text)
        self.callback_query = None
        self.effective_user = SimpleNamespace(id=1)


class DummyContext:
    def __init__(self, user_data=None, args=None):
        self.user_data = user_data or {}
        self.args = args or []


@pytest.mark.asyncio
@pytest.mark.parametrize("field,value", [
    ("label", "NewLabel"),
    ("category", "smart"),
    ("tags", "tag1,tag2"),
    ("min_trade_size", "100"),
])
async def test_edit_wallet_value_builds_query(monkeypatch, field, value):
    bot = DummyBot()
    wm = WalletManager(bot)

    exec_mock = AsyncMock()
    monkeypatch.setattr(db_module.db, 'execute', exec_mock)

    update = DummyUpdate(value)
    context = DummyContext({'edit_field': field, 'edit_wallet': '0xabc'})

    await wm.edit_wallet_value(update, context)

    column = FIELD_MAP[field]
    exec_mock.assert_awaited_once_with(
        f"UPDATE tracked_wallets SET {column}=$1 WHERE wallet_address=$2",
        value,
        '0xabc'
    )
    assert update.message.replies[0][0] == "Updated"


@pytest.mark.asyncio
async def test_list_wallets_formatting(monkeypatch):
    bot = DummyBot()
    wm = WalletManager(bot)

    sample_wallets = [
        {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'label': 'Alpha',
            'category': 'whale',
            'tags': ['vip'],
            'tracking_enabled': True,
            'total_trades': 10,
            'total_pnl': 1000.5,
            'win_rate': 60.0,
            'last_activity': None,
        },
        {
            'wallet_address': '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
            'label': 'Beta',
            'category': 'smart',
            'tags': None,
            'tracking_enabled': False,
            'total_trades': None,
            'total_pnl': None,
            'win_rate': None,
            'last_activity': None,
        },
    ]
    fetch_mock = AsyncMock(return_value=sample_wallets)
    fetchval_mock = AsyncMock(return_value=len(sample_wallets))
    monkeypatch.setattr(db_module.db, 'fetch', fetch_mock)
    monkeypatch.setattr(db_module.db, 'fetchval', fetchval_mock)

    update = DummyUpdate()
    context = DummyContext()

    await wm.list_wallets_command(update, context)

    expected = (
        f"Tracked Wallets ({len(sample_wallets)} total)\n\n"
        "🟢 Alpha (whale)\n"
        "`0x1234...5678`\n"
        "📈 PnL: $1,000.50 | Win Rate: 60.0% | Trades: 10\n"
        "Tags: vip\n\n"
        "🔴 Beta (smart)\n"
        "`0xabcd...abcd`\n\n"
    )
    sent_text = update.message.replies[0][0]
    assert sent_text == expected
