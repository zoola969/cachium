# Utilities

Utilities provide small building blocks used across the library.

## CacheWith

CacheWith is a marker used in type annotations to indicate that a parameter participates in the cache key. Use it to include only the arguments that affect determinism and exclude framework or context objects.

::: cachium._helpers.CacheWith
