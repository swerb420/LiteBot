# src/async_task_supervisor.py

import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_with_retry(task_coro):
    while True:
        try:
            await task_coro()
        except Exception as e:
            logger.error(f"[Supervisor] Task failed: {e}. Restarting...")
            await asyncio.sleep(5)
