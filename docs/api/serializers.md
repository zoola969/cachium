# Serializers

Serializers convert function arguments into stable strings used inside cache keys. Pick a serializer that is deterministic for your value types and context. ReprSerializer is a good default; Md5Serializer creates compact hashes useful for long or sensitive keys.

When to use which:
- ReprSerializer: readable, good for debugging.
- StrSerializer: for values with meaningful __str__.
- StdHashSerializer: leverages Python's hash where appropriate.
- Md5Serializer: fixed-length digest for shorter keys or cross-process stability.

Related pages: Key Builders and Concepts. Full reference below.

::: cachium.serializers._abc.Serializer

---

::: cachium.serializers._repr.ReprSerializer

---

::: cachium.serializers._str.StrSerializer

---

::: cachium.serializers._std_hash.StdHashSerializer
