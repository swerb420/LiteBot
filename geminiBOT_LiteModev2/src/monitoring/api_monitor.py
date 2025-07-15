import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)

class ApiMonitor:
    async def run(self):
        while True:
            logger.info("[ApiMonitor] heartbeat")
            await asyncio.sleep(600)
