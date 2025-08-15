# Tutorials

This section contains step-by-step guides for common workflows.

## 1. Configure TTL and max size

```python
from datetime import timedelta
from py_cashier import cache
from py_cashier.storages.ttl_map import TTLMapStorage

@cache(storage=lambda: TTLMapStorage(max_size=1000, ttl=timedelta(minutes=10)))
def get_item(key: str) -> str:
    return f"value:{key}"
```

## 2. Cache only specific arguments (type-annotated)

```python
from typing import Annotated
from py_cashier import cache, CacheWith
from py_cashier.storages.ttl_map import TTLMapStorage

# Cache only by `x`, ignore `y` in the cache key
@cache(storage=lambda: TTLMapStorage())
def f_cached(x: Annotated[int, CacheWith()], y: int) -> int:
    return x + y
```
