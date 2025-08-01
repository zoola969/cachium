from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    """Defines an abstract base class for serializing objects into string format.

    This class enforces the implementation of object serialization methods in subclasses,
    allowing for flexible and consistent transformation of any data type into string format.

    """

    @classmethod
    @abstractmethod
    def serialize(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
