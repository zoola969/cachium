from typing import Any

from ._abc import Serializer


class StrSerializer(Serializer):
    """Serializer class for converting objects to strings.

    This class provides functionality to convert any given value
    to its string representation. It can be used wherever a
    string conversion is required in serialization or other
    similar operations.

    ## Example

    ```python
    from cachium.serializers import StrSerializer

    StrSerializer.serialize(123)  # returns '123'

    from datetime import datetime
    StrSerializer.serialize(datetime(2000, 1, 1))  # returns '2000-01-01 00:00:00'

    ```
    """

    @classmethod
    def serialize(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return str(value)
