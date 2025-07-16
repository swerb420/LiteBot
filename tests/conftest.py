import sys
from types import SimpleNamespace

# Provide stub aioredis to avoid import errors on Python 3.12
sys.modules.setdefault('aioredis', SimpleNamespace(
    RedisError=Exception,
    from_url=lambda *a, **k: SimpleNamespace()
))
