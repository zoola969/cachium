from typing import Any

from ._abc import KeySerializer


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
