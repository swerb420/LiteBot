import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import types

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from data_ingestion import reddit_scraper as rs

@pytest.mark.asyncio
async def test_run_logs_and_continues_on_redis_error(monkeypatch):
    scraper = rs.RedditScraper()
    get_mock = AsyncMock(side_effect=rs.redis.RedisError('fail'))
    set_mock = AsyncMock()
    scraper.redis = SimpleNamespace(get=get_mock, set=set_mock)

    logged = []
    monkeypatch.setattr(rs, 'logger', SimpleNamespace(info=lambda *a, **k: None,
                                                      exception=lambda msg: logged.append(msg)))

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(rs.asyncio, 'sleep', fake_sleep)

    with pytest.raises(KeyboardInterrupt):
        await scraper.run()

    assert logged and 'fail' in logged[0]
    get_mock.assert_awaited_once()
    set_mock.assert_awaited_once()
