# === 3️⃣ src/onchain/gmx_decoder.py ===
# ➜ Location: src/onchain/gmx_decoder.py
from web3 import Web3
from utils.logger import get_logger

logger = get_logger(__name__)

GMX_VAULT_ABI = []  # Add real GMX ABI JSON here later

class GMXDecoder:
    def __init__(self):
        self.w3 = Web3()
        self.vault = self.w3.eth.contract(abi=GMX_VAULT_ABI)

    def decode_position_open(self, log):
        try:
            decoded = self.vault.events.IncreasePosition().processLog(log)
            return decoded
        except Exception as e:
            logger.error(f"[GMXDecoder] decode failed: {e}")
            return None

