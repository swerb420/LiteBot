import asyncio
from typing import Any, Dict


class InMemoryCache:
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.expiry: Dict[str, float] = {}
        self.lock = asyncio.Lock()

    async def set(self, key: str, value: Any, ttl: int = 0):
        async with self.lock:
            self.store[key] = value
            if ttl:
                self.expiry[key] = asyncio.get_event_loop().time() + ttl
            elif key in self.expiry:
                del self.expiry[key]

    async def get(self, key: str) -> Any:
        async with self.lock:
            if (
                key in self.expiry
                and self.expiry[key] < asyncio.get_event_loop().time()
            ):
                self.store.pop(key, None)
                self.expiry.pop(key, None)
                return None
            return self.store.get(key)


cache = InMemoryCache()
