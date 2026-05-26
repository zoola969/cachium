# Key Builders

Key builders construct the cache key for a given function call. The `DefaultKeyBuilder` uses the function file path, function name, and selected arguments (by default all args/kwargs) serialized via a serializer (`repr` by default). Choose a custom builder when you need to exclude framework objects, add prefixes/versions, or change serialization.

The `cache` decorator accepts a key-builder factory: a callable that returns a `KeyBuilder` instance. Classes with no required constructor arguments work directly, for example `key_builder=MyKeyBuilder`.

Common parameters (DefaultKeyBuilder):
- func: the original function; used to extract signature and names.
- key_serializer: `Serializer` type used to turn values into stable strings (e.g., `ReprSerializer`, `Md5Serializer`).
- prefix: optional string to namespace or version keys.
- delimiter: string used between argument key/value pairs.

Related pages: Concepts (key model), Examples (custom builders), and Serializers. Full reference below.

::: cachium.key_builders._abc.KeyBuilder

---

::: cachium.key_builders._default.DefaultKeyBuilder
