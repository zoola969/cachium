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
from cachium import cache

# Simple function caching
@cache()
def expensive_calculation(x: int, y: int) -> int:
    print(f"Calculating {x} + {y}")
    return x + y

# First call performs the calculation
result1 = expensive_calculation(1, 2)  # Output: Calculating 1 + 2
print(result1)  # Output: 3

# Second call uses cached result
result2 = expensive_calculation(1, 2)  # No calculation performed
print(result2)  # Output: 3

# Async function caching works too
@cache()
async def async_expensive_calculation(x: int, y: int) -> int:
    print(f"Calculating {x} + {y} asynchronously")
    return x + y

# Usage with async functions
import asyncio

async def main():
    # First call performs the calculation
    result1 = await async_expensive_calculation(1, 2)
    # Second call uses cached result
    result2 = await async_expensive_calculation(1, 2)

    print(result1, result2)  # Output: 3 3

asyncio.run(main())
```

## Advanced Usage

### Custom TTL and Cache Size

```python
from datetime import timedelta
from cachium import cache
from cachium._storages import TTLMapStorage

@cache(storage=lambda: TTLMapStorage(max_size=100, ttl=timedelta(hours=1)))
def long_lived_cache_function(x):
    return x * 2
```

### Custom Key Builders

```python
from cachium import cache, DefaultKeyBuilder

# Create a custom key builder
key_builder = DefaultKeyBuilder(
    prefix="custom_prefix",
    func=lambda x, y: x + y,
    delimiter=":"
)

@cache(key_builder=key_builder)
def my_function(x, y):
    return x + y
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
