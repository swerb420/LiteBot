import os
from utils.logger import get_logger

logger = get_logger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/db')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
ALCHEMY_WS_URL = os.getenv('ALCHEMY_WS_URL', '')
GMX_VAULT_ADDRESS = os.getenv('GMX_VAULT_ADDRESS', '0x0000000000000000000000000000000000000000')


def setup_logging():
    # Logging already configured in utils.logger
    logger.info("[Settings] Logging configured")
