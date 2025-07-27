from abc import ABC, abstractmethod
from typing import Any


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
