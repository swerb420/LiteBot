import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import types

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from data_ingestion import news_aggregator as na


@pytest.mark.asyncio
async def test_update_news_sets_cache(monkeypatch):
    aggregator = na.NewsAggregator()
    set_mock = AsyncMock()
    aggregator.redis = SimpleNamespace(set=set_mock)
    monkeypatch.setattr(aggregator, 'fetch_all', AsyncMock(return_value='a\nb'))
    await aggregator.update_news()
    set_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_all_collects_titles(monkeypatch):
    entries1 = [SimpleNamespace(title='A'), SimpleNamespace(title='B')]
    entries2 = [SimpleNamespace(title='C')]

    def fake_parse(url):
        return SimpleNamespace(entries=entries1 if 'bbc' in url else entries2)

    monkeypatch.setattr(na.feedparser, 'parse', fake_parse)
    aggregator = na.NewsAggregator()
    data = await aggregator.fetch_all()
    assert 'A' in data and 'C' in data


@pytest.mark.asyncio
async def test_alert_cached_news_sends(monkeypatch):
    send_mock = AsyncMock()
    aggregator = na.NewsAggregator(tg_bot=SimpleNamespace(send_alert=send_mock))
    aggregator.redis = SimpleNamespace(get=AsyncMock(return_value='abc'))
    await aggregator.alert_cached_news()
    send_mock.assert_awaited_once_with('abc')
