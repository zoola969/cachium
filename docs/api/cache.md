# Cache Decorator

The cache decorator wraps a function and stores results in a configured storage, keyed by a deterministic cache key. Use it when you want per-function memoization with TTL, LRU, and dog‑piling prevention.

When to use:
- You need function-level caching inside a process (sync or async).
- You want TTL-based staleness control and LRU eviction.
- You want to avoid thundering herds via per-key locks.

Common parameters:
- storage: required callable returning the storage instance (`TTLMapStorage` for sync, `TTLMapAsyncStorage` for async).
- key_builder: optional callable returning a `KeyBuilder` to customize how keys are built (which args participate, serialization, prefixes, etc.).

The storage factory is called once at decoration time, so each decorated function gets its own storage instance. Passing a sync storage to an async function, or an async storage to a sync function, raises `TypeError`.

See also: Quickstart, Concepts, and Examples pages. Full reference below.

::: cachium._decorators.cache
