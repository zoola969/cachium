import hashlib
from typing import Any

from typing_extensions import override

from ._abc import Serializer


class Md5Serializer(Serializer):
    """Serializer class that provides MD5 hash-based serialization of objects.

    This class extends the base Serializer and implements serialization
    using MD5 hashing algorithm, which provides consistent hash values
    across different Python processes and sessions.
    """

    @override
    @classmethod
    def serialize(cls, value: Any) -> str:
        """Convert value to string using MD5 hash."""
        return hashlib.md5(str(value).encode(), usedforsecurity=False).hexdigest()
