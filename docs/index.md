# py-cashier

Sync and async cache with TTL and LRU support.

## Features

- Time-to-live (TTL) support for cache entries
- Least Recently Used (LRU) eviction policy
- Both synchronous and asynchronous API
- Type-safe with full typing support
- Customizable key builders and serializers

## Installation
bash pip install py-cashier

## Quick Start

```python
from py_cashier import cache

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
```

## License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

You can continue by adding content to the other documentation files based on your package functionality. The API reference section should document your public API, including the main classes and functions like:
- CacheWith
- DefaultKeyBuilder
- KeyBuilder
- Serializer and its implementations
- The cache decorator

Remember to install the required packages from your `docs` optional dependencies:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

To build and preview your documentation locally, run:

```bash
mkdocs serve
```

This will start a local server, typically at http://127.0.0.1:8000/, where you can preview your documentation as you develop it.
