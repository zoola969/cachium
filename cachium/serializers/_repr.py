from typing import Any

from typing_extensions import override

from ._abc import Serializer


class ReprSerializer(Serializer):
    """A serializer class for converting values to string using their `repr` representation.

    The purpose of this class is to provide a specific serialization mechanism
    where the `repr` representation of the object is used instead of the
    standard `str` conversion. This is particularly useful for debugging or
    logging where precise and unambiguous object representations are required.

    ## Example

    ```python
    from cachium.serializers import ReprSerializer

    ReprSerializer.serialize("test")  # returns "'test'"

    from datetime import datetime
    ReprSerializer.serialize(datetime(2000, 1, 1))  # returns 'datetime.datetime(2000, 1, 1, 0, 0)'
    ```
    """

    @override
    @classmethod
    def serialize(cls, value: Any) -> str:
        """Convert value to string."""
        return repr(value)
