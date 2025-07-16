import asyncio
from prometheus_client import Counter, start_http_server
from utils.logger import get_logger

logger = get_logger(__name__)

REQUESTS_COUNTER = Counter('bot_requests_total', 'Total requests processed')

class MetricsServer:
    def __init__(self, port: int = 8000):
        self.port = port

    async def run(self):
        start_http_server(self.port)
        logger.info(f"[MetricsServer] running on port {self.port}")
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("[MetricsServer] shutdown")
            raise

