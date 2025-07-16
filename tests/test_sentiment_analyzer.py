import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, AsyncMock
import json
import types
import pytest

sys.modules['aioredis'] = types.SimpleNamespace(
    RedisError=Exception,
    from_url=lambda *a, **k: SimpleNamespace()
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from ai_analysis.sentiment_mobilebert import SentimentAnalyzer

@pytest.mark.asyncio
async def test_analyze_success(monkeypatch):
    analyzer = SentimentAnalyzer()
    analyzer._loaded = True
    analyzer.pipeline = MagicMock(return_value=[{'label': 'POS', 'score': 0.9}])
    get_mock = AsyncMock(return_value=None)
    set_mock = AsyncMock()
    analyzer.redis = SimpleNamespace(get=get_mock, set=set_mock)

    result = await analyzer.analyze('great')

    assert result == {'label': 'POS', 'score': 0.9}
    get_mock.assert_awaited_once()
    set_mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_analyze_exception(monkeypatch):
    analyzer = SentimentAnalyzer()
    analyzer._loaded = True
    analyzer.pipeline = MagicMock(side_effect=RuntimeError('fail'))
    get_mock = AsyncMock(return_value=None)
    set_mock = AsyncMock()
    analyzer.redis = SimpleNamespace(get=get_mock, set=set_mock)
    logged = []
    monkeypatch.setattr('ai_analysis.sentiment_mobilebert.logger', SimpleNamespace(error=lambda msg: logged.append(msg)))
    result = await analyzer.analyze('bad')
    assert result == {'label': 'NEUTRAL', 'score': 0.5}
    assert logged and 'fail' in logged[0]

    set_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_analyze_cached(monkeypatch):
    analyzer = SentimentAnalyzer()
    analyzer._loaded = True
    analyzer.pipeline = MagicMock()
    cached = {'label': 'NEG', 'score': 0.1}
    get_mock = AsyncMock(return_value=json.dumps(cached))
    set_mock = AsyncMock()
    analyzer.redis = SimpleNamespace(get=get_mock, set=set_mock)

    result = await analyzer.analyze('meh')

    assert result == cached
    analyzer.pipeline.assert_not_called()
    set_mock.assert_not_awaited()
