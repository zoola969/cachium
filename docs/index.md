# cachium

Sync and async caching for Python with TTL and LRU, plus per-key locks to prevent dog‑piling.

## Why cachium?
- Prevents thundering herds: only one caller computes per key; others wait and reuse.
- Works everywhere: thread-safe for sync, asyncio-safe for async.
- Deterministic keys: selective argument participation via CacheWith, or custom builders/serializers.
- Fast in-memory storage with TTL and LRU.

## Features

- Time-to-live (TTL) support for cache entries
- Least Recently Used (LRU) eviction policy
- Both synchronous and asynchronous API
- Type-safe with full typing support
- Customizable key builders and serializers

## Installation
```bash
pip install cachium
```

## Quick Start

```python
from datetime import timedelta
from cachium import cache
from cachium.storages.ttl_map import TTLMapStorage

@cache(storage=TTLMapStorage.create_with(max_size=1024, ttl=timedelta(minutes=1)))
def add(a: int, b: int) -> int:
    return a + b

# Simple function caching
@cache()
def expensive_calculation(x: int, y: int) -> int:
    print(f"Calculating {x} + {y}")
    return x + y

Async:
```python
import asyncio
from datetime import timedelta
from cachium import cache
from cachium.storages.ttl_map import TTLMapAsyncStorage

# Second call uses cached result
result2 = expensive_calculation(1, 2)  # No calculation performed
print(result2)  # Output: 3
```

## License
This project is licensed under the Apache License 2.0 — see [LICENSE](https://github.com/zoola969/cachium/blob/main/LICENSE).
