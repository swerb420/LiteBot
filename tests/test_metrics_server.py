import asyncio
import urllib.request
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'geminiBOT_LiteModev2' / 'src'))

from monitoring.metrics_server import MetricsServer

@pytest.mark.asyncio
async def test_metrics_endpoint():
    server = MetricsServer(port=9100)
    task = asyncio.create_task(server.run())
    await asyncio.sleep(0.2)
    data = urllib.request.urlopen('http://localhost:9100/metrics').read().decode()
    assert 'python_gc_objects_collected_total' in data
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

