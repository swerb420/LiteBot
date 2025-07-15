import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

class SystemMonitor:
    async def run(self):
        while True:
            logger.info("[SystemMonitor] heartbeat")
            await asyncio.sleep(600)
