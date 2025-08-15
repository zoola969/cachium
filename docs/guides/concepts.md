# Concepts

This page explains the core concepts behind py-cashier so you can reason about cache hits, misses, and correctness in your application.

## Cache key model
- What becomes the key: By default, keys are built from the fully qualified function name and its arguments. The default builder serializes each participating argument using a stable serializer (repr-based by default) to form a deterministic string key.
- Selective arguments: Use the CacheWith type annotation to mark which parameters should participate in the key. This helps avoid including non-deterministic or heavy framework objects (e.g., requests, DB sessions) that would explode key cardinality.
- Custom builders and serializers: Provide your own KeyBuilder to control which args/kwargs and in what order are included, and plug different serializers (e.g., MD5) when you need shorter or cross-process-stable keys.

## Storage model
- In-memory TTL + LRU: The built-in TTLMapStorage/TTLMapAsyncStorage keep values in-memory with time-to-live expiration and a least-recently-used eviction policy when max_size is reached.
- Sizing: max_size bounds the number of cached entries. When the cache is full, the least recently used entries are evicted first. TTL expiration removes entries after their time window passes.
- Fit for purpose: In-memory storages are ideal for function-level caching within a single process. For multi-process or cross-machine caches, use an external store (e.g., Redis) — planned for future releases.

## Concurrency model
- Per-key locking: py-cashier prevents dog-piling by ensuring only one caller computes a missing value per key. Others wait and reuse the result. This applies to both sync and async flows with appropriate lock types.
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
