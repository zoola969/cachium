# cachium

Sync and async cache

## Features

- Both synchronous and asynchronous API
- Type-safe with full typing support
- Customizable key builders and serializers
- Thread-safe and coroutine-safe with dog-piling prevention

## Installation

```bash
pip install cachium
```

## Quick Start

```python
import asyncio

from cachium import cache
from cachium.storages.ttl_map import TTLMapStorage, TTLMapAsyncStorage

# Simple function caching
@cache(storage=TTLMapStorage.create_with(max_size=100, ttl=None))
def expensive_calculation(x: int, y: int) -> int:
    return x + y

# First call performs the calculation
result1 = expensive_calculation(1, 2)  # Output: Calculating 1 + 2
print(result1)  # Output: 3

# Second call uses cached result
result2 = expensive_calculation(1, 2)  # No calculation performed
print(result2)  # Output: 3

# Async function caching works too
@cache(storage=TTLMapAsyncStorage.create_with(max_size=100, ttl=None))
async def async_io_operation(x: int, y: int) -> int:
    await asyncio.sleep(1)  # Simulate an I/O-bound operation
    return x + y


async def main():
    # First call performs the calculation
    result1 = await async_io_operation(1, 2)
    # Second call uses cached result
    result2 = await async_io_operation(1, 2)

    print(result1, result2)  # Output: 3 3

asyncio.run(main())
```

## Advanced Usage

### Custom TTL and Cache Size

```python
from datetime import timedelta
from cachium import cache
from cachium.storages.ttl_map import TTLMapStorage

@cache(storage=TTLMapStorage.create_with(max_size=100, ttl=timedelta(hours=1)))
def long_lived_cache_function(x):
    return x * 2
```

## License

See the LICENSE file for details.
