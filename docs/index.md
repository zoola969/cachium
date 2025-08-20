# py-cashier

Sync and async caching for Python with TTL and LRU, plus per-key locks to prevent dog‑piling.

## Why py-cashier?
- Prevents thundering herds: only one caller computes per key; others wait and reuse.
- Works everywhere: thread-safe for sync, asyncio-safe for async.
- Deterministic keys: selective argument participation via CacheWith, or custom builders/serializers.
- Fast in-memory storage with TTL and LRU.

## Features
- Sync and async function caching
- TTL expiration and LRU eviction
- Per-key locking (dog‑piling prevention)
- Typed API, small surface area
- Selective keying via CacheWith

## Installation
```bash
pip install py-cashier
```

## Quickstart (2 minutes)
Sync:
```python
from datetime import timedelta
from py_cashier import cache
from py_cashier.storages.ttl_map import TTLMapStorage

@cache(storage=lambda: TTLMapStorage(max_size=1024, ttl=timedelta(minutes=1)))
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))    # computes
print(add(1, 2))    # cached
```

Async:
```python
import asyncio
from datetime import timedelta
from py_cashier import cache
from py_cashier.storages.ttl_map import TTLMapAsyncStorage

@cache(storage=lambda: TTLMapAsyncStorage(max_size=512, ttl=timedelta(seconds=30)))
async def add_async(a: int, b: int) -> int:
    return a + b

asyncio.run(add_async(1, 2))
asyncio.run(add_async(1, 2))  # cached
```

## What’s New
- See the full changelog: [Changelog](changelog.md)

## Where to next?
- Start here: [Quickstart](guides/quickstart.md)
- Understand the model: [Concepts](guides/concepts.md)
- Use the building blocks: [API Reference](api/index.md)
- Browse [Examples](examples.md)

## License
This project is licensed under the Apache License 2.0 — see [LICENSE](https://github.com/zoola969/py-cashier/blob/main/LICENSE).
