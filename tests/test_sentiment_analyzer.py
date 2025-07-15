import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from ai_analysis.sentiment_mobilebert import SentimentAnalyzer

@pytest.mark.asyncio
async def test_analyze_success(monkeypatch):
    analyzer = SentimentAnalyzer()
    analyzer._loaded = True
    analyzer.pipeline = MagicMock(return_value=[{'label': 'POS', 'score': 0.9}])
    result = await analyzer.analyze('great')
    assert result == {'label': 'POS', 'score': 0.9}

@pytest.mark.asyncio
async def test_analyze_exception(monkeypatch):
    analyzer = SentimentAnalyzer()
    analyzer._loaded = True
    analyzer.pipeline = MagicMock(side_effect=RuntimeError('fail'))
    logged = []
    monkeypatch.setattr('ai_analysis.sentiment_mobilebert.logger', SimpleNamespace(error=lambda msg: logged.append(msg)))
    result = await analyzer.analyze('bad')
    assert result == {'label': 'NEUTRAL', 'score': 0.5}
    assert logged and 'fail' in logged[0]
