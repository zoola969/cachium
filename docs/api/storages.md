# Storages

Storages keep cached values and provide the per-key locks used by the decorator to prevent dog-piling.

Built-in storages:
- `TTLMapStorage`: synchronous in-memory storage with TTL expiration and LRU eviction.
- `TTLMapAsyncStorage`: asynchronous counterpart for `async def` functions.

Usage:

```python
from datetime import timedelta
from cachium import cache
from cachium.storages.ttl_map import TTLMapStorage

@cache(storage=TTLMapStorage.create_with(max_size=1000, ttl=timedelta(minutes=5)))
def get_value(key: str) -> str:
    return f"value:{key}"
```

Important details:
- `cache` expects a storage factory, not a storage instance.
- The factory is called once at decoration time, giving each decorated function its own storage.
- Use `TTLMapStorage` for regular functions and `TTLMapAsyncStorage` for async functions.
- `max_size` limits entry count; `ttl` controls age-based expiration. Use `ttl=None` to disable age-based expiration.
- Built-in storages are process-local. Use a custom storage backend for shared multi-process or cross-machine caching.

Full reference below.

::: cachium.storages._abc.Result

---

::: cachium.storages._abc.BaseStorage

---

::: cachium.storages._abc.BaseAsyncStorage

---

::: cachium.storages.ttl_map.TTLMapStorage

---

::: cachium.storages.ttl_map.TTLMapAsyncStorage
