# Concepts

This page explains the core concepts behind cachium so you can reason about cache hits, misses, and correctness in your application.

## Cache key model
- What becomes the key: By default, keys are built from the function file path, function name, and arguments. The default builder serializes each participating argument using `repr()` to form a deterministic string key.
- Selective arguments: Use the `CacheWith` type annotation to mark which parameters should participate in the key. If any parameter is marked, only marked parameters are included. This helps avoid non-deterministic or heavy framework objects such as requests or DB sessions.
- Custom builders and serializers: Provide your own `KeyBuilder` factory to control which args/kwargs are included and how they are serialized. Use serializers such as `Md5Serializer` when you need compact keys.

## Storage model
- In-memory TTL + LRU: The built-in `TTLMapStorage` and `TTLMapAsyncStorage` keep values in-memory with time-to-live expiration and a least-recently-used eviction policy when `max_size` is reached.
- Sizing: `max_size` bounds the number of cached entries. When the cache is full, the least recently used entries are evicted first. TTL expiration removes entries after their time window passes. Set `ttl=None` for entries that do not expire by age.
- Storage factories: The `cache` decorator expects a callable that creates storage, for example `TTLMapStorage.create_with(...)`. The factory is called once at decoration time, so each decorated function gets its own storage instance.
- Fit for purpose: In-memory storages are ideal for function-level caching within a single process. For multi-process or cross-machine caches, use an external store (e.g., Redis) — planned for future releases.

## Concurrency model
- Per-key locking: cachium prevents dog-piling by ensuring only one caller computes a missing value per key. Others wait and reuse the result. This applies to both sync and async flows with appropriate lock types.
- Safety: The decorator verifies that sync functions use a sync storage and async functions use an async storage to avoid accidental cross-usage.
- Granularity: Locks are per-key, so independent keys proceed in parallel.

## Invalidation strategies
- TTL: Set an appropriate TTL for data that naturally becomes stale after a period.
- Direct delete by key: With a custom storage integration, you can remove entries by their constructed key (useful for precise invalidation hooks).
- Prefix rotation / versioned keys: Add a version or prefix component to your keys; bump it to invalidate a whole class of entries at once.

See also:
- Quickstart: ../guides/quickstart.md
- API overview: ../api/index.md
- Examples: ../examples.md
