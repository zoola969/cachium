# Key Builders

Key builders construct the cache key for a given function call. The DefaultKeyBuilder uses the function path and selected arguments (by default all args/kwargs) serialized via a serializer (repr by default). Choose a custom builder when you need to exclude framework objects, add prefixes/versions, or change serialization.

Common parameters (DefaultKeyBuilder):
- func: the original function; used to extract signature and names.
- key_serializer: Serializer type used to turn values into stable strings (e.g., ReprSerializer, Md5Serializer).
- prefix: optional string to namespace or version keys.

Related pages: Concepts (key model), Examples (custom builders), and Serializers. Full reference below.

::: cachium.key_builders._abc.KeyBuilder

---

::: cachium.key_builders._default.DefaultKeyBuilder
