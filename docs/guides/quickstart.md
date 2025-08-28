# Quickstart

This quickstart shows the typical usage pattern.

Notes:
- Dog-piling protection: per-key locks ensure only one caller computes a missing value.
- Safe by design: thread-safe for sync functions and asyncio-safe for async functions.
- Deterministic keys: build keys from selected arguments using CacheWith or a custom key builder.

## Sync function

```python
from datetime import timedelta
from py_cashier import cache
from py_cashier.storages.ttl_map import TTLMapStorage

# Configure TTL and max size
@cache(storage=TTLMapStorage.create_with(max_size=512, ttl=timedelta(seconds=30)))
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))
print(add(1, 2))  # cached
```

## Async function

```python
import asyncio
from datetime import timedelta
from py_cashier import cache
from py_cashier.storages.ttl_map import TTLMapAsyncStorage

# Configure TTL and max size for async storage
@cache(storage=TTLMapAsyncStorage.create_with(max_size=512, ttl=timedelta(seconds=30)))
async def add_async(a: int, b: int) -> int:
    # Simulate I/O
    await asyncio.sleep(0.1)
    return a + b

async def main():
    print(await add_async(1, 2))
    print(await add_async(1, 2))  # cached

asyncio.run(main())
```

## Cache only specific arguments using CacheWith

```python
from typing import Annotated
from py_cashier import cache, CacheWith
from py_cashier.storages.ttl_map import TTLMapStorage

# Only `x` participates in the cache key; calls differing only by `y` share the cached result
@cache(storage=TTLMapStorage.create_with())
def compute(x: Annotated[int, CacheWith()], y: int) -> int:
    return x + y

compute(1, 10)   # computes and caches by x=1
compute(1, 999)  # served from cache (same x)
```
