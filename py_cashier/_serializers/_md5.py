import hashlib
from typing import Any

from ._abc import KeySerializer


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
