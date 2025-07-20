from typing import Any

from ._abc import KeySerializer


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
