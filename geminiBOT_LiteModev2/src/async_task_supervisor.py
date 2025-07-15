# src/async_task_supervisor.py

import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

async def run_with_retry(task_coro, *, base_delay: float = 5, max_delay: float = 60,
                        reset_time: float = 60):
    """Run a coroutine forever, restarting on failure.

    Parameters
    ----------
    task_coro : Callable[[], Awaitable]
        The coroutine to run.
    base_delay : float, optional
        Initial delay between restarts, by default 5 seconds.
    max_delay : float, optional
        Maximum delay after repeated failures, by default 60 seconds.
    reset_time : float, optional
        If the task runs for at least this many seconds before failing,
        the delay is reset to ``base_delay``.
    """

    delay = 0
    while True:
        start_time = asyncio.get_event_loop().time()
        try:
            await task_coro()
        except Exception as e:
            run_time = asyncio.get_event_loop().time() - start_time
            if run_time >= reset_time:
                next_delay = base_delay
            else:
                next_delay = base_delay if delay == 0 else min(delay * 2, max_delay)
            logger.error(
                f"[Supervisor] Task failed: {e}. Restarting in {next_delay} seconds..."
            )
            await asyncio.sleep(next_delay)
            delay = next_delay
        else:
            delay = base_delay
