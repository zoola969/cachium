import hashlib
from abc import ABC, abstractmethod
from collections.abc import Hashable
from typing import Any

from typing_extensions import TypeAlias


class KeySerializer(ABC):
    """Defines an abstract base class for serializing keys into string format.

    This class enforces the implementation of key serialization methods in subclasses,
    allowing for flexible and consistent transformation of any data type into string
    format for use in various applications.

    """

    @classmethod
    @abstractmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""


class StrKeySerializer(KeySerializer):
    """A serializer class for converting keys to strings.

    This class provides functionality to convert any given value
    to its string representation. It can be used wherever a
    string key conversion is required in serialization or other
    similar operations.

    ## Example

    ```python
    from py_cashier import StrKeySerializer

    serializer = StrKeySerializer()

    serializer.to_str(123)  # returns '123'

    from datetime import datetime
    serializer.to_str(datetime(2000, 1, 1))  # returns '2000-01-01 00:00:00'

    ```
    """

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return str(value)


class ReprKeySerializer(KeySerializer):
    """A serializer class for converting values to string using their `repr` representation.

    The purpose of this class is to provide a specific serialization mechanism
    where the `repr` representation of the object is used instead of the
    standard `str` conversion. This is particularly useful for debugging or
    logging where precise and unambiguous object representations are required.

    ## Example

    ```python
    from py_cashier import ReprKeySerializer

    serializer = ReprKeySerializer()
    serializer.to_str("test")  # returns "'test'"

    from datetime import datetime
    serializer.to_str(datetime(2000, 1, 1))  # returns 'datetime.datetime(2000, 1, 1, 0, 0)'
    ```
    """

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return repr(value)


class StdHashKeySerializer(KeySerializer):
    """A key serializer class that provides methods to serialize values as hashed strings.

    This class extends the base KeySerializer and overrides its behavior
    by serializing the given value through hashing and then converting
    the hash to a string. It is intended to handle cases where values
    need to be safely serialized with a consistent hash-based identifier.

    Warning:
        The Python `hash()` function used by this serializer is not guaranteed to
        return the same value for the same input across different Python processes
        or interpreter sessions. For cache persistence across processes, consider
        using a different serialization method like `Md5KeySerializer`.

    ## Example

    ```python
    from py_cashier import StdHashKeySerializer

    serializer = StdHashKeySerializer()

    serializer.to_str(123)  # returns a hash value like '1561442120842248018'

    from datetime import datetime
    serializer.to_str(datetime(2000, 1, 1))  # returns a hash value like '5826678583026451935'

    serializer.to_str([1,2,3])  # raises TypeError: unhashable type: 'list'

    # Note: Actual hash values will vary between Python sessions
    ```

    """

    @classmethod
    def to_str(cls, value: Hashable) -> str:
        """Convert value to string."""
        return str(hash(value))


class Md5KeySerializer(KeySerializer):
    """A key serializer class that provides MD5 hash-based serialization of values.

    This class extends the base KeySerializer and implements serialization
    using MD5 hashing algorithm, which provides consistent hash values
    across different Python processes and sessions.
    """

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string using MD5 hash."""
        return hashlib.md5(str(value).encode(), usedforsecurity=False).hexdigest()


CacheKey: TypeAlias = str
