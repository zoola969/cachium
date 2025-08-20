# API Reference Overview

This section explains the main building blocks and links to their detailed reference. Start with the cache decorator, then dig into key builders and serializers to control how keys are produced. Storages define how values are kept and locked.

- Cache: Use the decorator to cache sync/async functions; configure storage and key building.
- Key builders: Choose which args/kwargs become part of the key and how they are serialized.
- Serializers: Control determinism and key length/compatibility.
- Storages: In-memory TTL + LRU storages (sync/async) and shared abstractions.

Tip: After reading the reference, see the [Examples](../examples.md) and [Quickstart](../guides/quickstart.md) for runnable snippets.
