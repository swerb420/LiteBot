import sys
from pathlib import Path
import asyncio
import pytest

# add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import async_task_supervisor as ats
from async_task_supervisor import run_with_retry

@pytest.mark.asyncio
async def test_exponential_backoff(monkeypatch):
    sleeps = []
    fake_time = 0
    orig_sleep = asyncio.sleep

    async def fake_sleep(delay):
        nonlocal fake_time
        sleeps.append(delay)
        fake_time += delay
        await orig_sleep(0)

    class FakeLoop:
        def time(self):
            return fake_time

    monkeypatch.setattr(ats.asyncio, 'sleep', fake_sleep)
    monkeypatch.setattr(ats.asyncio, 'get_event_loop', lambda: FakeLoop())

    call_count = 0

    async def task():
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise RuntimeError('fail')
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        await run_with_retry(task, base_delay=1, max_delay=4, reset_time=10)

    assert sleeps == [1, 2, 4]

@pytest.mark.asyncio
async def test_backoff_resets_after_success(monkeypatch):
    sleeps = []
    fake_time = 0
    orig_sleep = asyncio.sleep

    async def fake_sleep(delay):
        nonlocal fake_time
        sleeps.append(delay)
        fake_time += delay
        await orig_sleep(0)

    class FakeLoop:
        def time(self):
            return fake_time

    monkeypatch.setattr(ats.asyncio, 'sleep', fake_sleep)
    monkeypatch.setattr(ats.asyncio, 'get_event_loop', lambda: FakeLoop())

    call_count = 0

    async def task():
        nonlocal call_count, fake_time
        call_count += 1
        if call_count <= 2:
            raise RuntimeError('fail')
        elif call_count == 3:
            fake_time += 6  # simulate long run
            raise RuntimeError('fail')
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        await run_with_retry(task, base_delay=1, max_delay=4, reset_time=5)

    assert sleeps == [1, 2, 1]
