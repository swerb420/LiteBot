# === 3️⃣ src/onchain/gmx_decoder.py ===
# ➜ Location: src/onchain/gmx_decoder.py
from web3 import Web3
from utils.logger import get_logger

logger = get_logger(__name__)

GMX_VAULT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "collateralToken", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "indexToken", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "sizeDelta", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "collateralDelta", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "averagePrice", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "entryFundingRate", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "reserveAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "markPrice", "type": "uint256"},
            {"indexed": False, "internalType": "bool", "name": "isLong", "type": "bool"},
            {"indexed": False, "internalType": "uint256", "name": "fee", "type": "uint256"},
        ],
        "name": "IncreasePosition",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "collateralToken", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "indexToken", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "sizeDelta", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "collateralDelta", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "averagePrice", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "entryFundingRate", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "reserveAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "markPrice", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "fee", "type": "uint256"},
            {"indexed": False, "internalType": "int256", "name": "realisedPnl", "type": "int256"},
            {"indexed": False, "internalType": "bool", "name": "isLong", "type": "bool"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
        ],
        "name": "DecreasePosition",
        "type": "event",
    },
]

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

    def decode_position_close(self, log):
        try:
            decoded = self.vault.events.DecreasePosition().processLog(log)
            return decoded
        except Exception as e:
            logger.error(f"[GMXDecoder] decode close failed: {e}")
            return None

