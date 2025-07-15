import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)


class EnsembleManager:
    """Manage coordination of lightweight AI modules."""

    async def run(self):
        logger.info("[EnsembleManager] Running...")
        while True:
            await asyncio.sleep(300)
