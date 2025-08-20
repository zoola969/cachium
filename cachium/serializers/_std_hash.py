from collections.abc import Hashable

from ._abc import Serializer


class StdHashSerializer(Serializer):
    """Serializer class that provides methods to serialize objects as hashed strings.

    This class extends the base Serializer and overrides its behavior
    by serializing the given value through hashing and then converting
    the hash to a string. It is intended to handle cases where values
    need to be safely serialized with a consistent hash-based identifier.

    Warning:
        The Python `hash()` function used by this serializer is not guaranteed to
        return the same value for the same input across different Python processes
        or interpreter sessions. For cache persistence across processes, consider
        using a different serialization method like `Md5Serializer`.

    ## Example

    ```python
    from cachium.serializers import StdHashSerializer

    StdHashSerializer.serialize(123)  # returns a hash value like '1561442120842248018'

    from datetime import datetime
    StdHashSerializer.serialize(datetime(2000, 1, 1))  # returns a hash value like '5826678583026451935'

    StdHashSerializer.serialize([1,2,3])  # raises TypeError: unhashable type: 'list'

    # Note: Actual hash values will vary between Python sessions
    ```

    """

    @classmethod
    def serialize(cls, value: Hashable) -> str:
        """Convert value to string."""
        return str(hash(value))
