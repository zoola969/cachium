from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, patch

import pytest

from cachium.serializers import Md5Serializer, ReprSerializer, Serializer, StdHashSerializer, StrSerializer


@pytest.mark.parametrize(
    ("serializer_class", "value", "expected"),
    [
        # StrSerializer tests
        (StrSerializer, 123, "123"),
        (StrSerializer, 123.45, "123.45"),
        (StrSerializer, "hello", "hello"),
        (StrSerializer, [1, 2, 3], "[1, 2, 3]"),
        (StrSerializer, {"a": 1, "b": 2}, "{'a': 1, 'b': 2}"),
        (StrSerializer, None, "None"),
        (
            StrSerializer,
            datetime(2000, 1, 1, tzinfo=None),  # noqa: DTZ001
            "2000-01-01 00:00:00",
        ),
        (
            StrSerializer,
            datetime(2000, 1, 1),  # noqa: DTZ001
            "2000-01-01 00:00:00",
        ),
        (
            StrSerializer,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
            "2000-01-01 00:00:00+00:00",
        ),
        # ReprSerializer tests
        (ReprSerializer, 123, "123"),
        (ReprSerializer, 123.45, "123.45"),
        (ReprSerializer, "hello", "'hello'"),  # Note the quotes
        (ReprSerializer, [1, 2, 3], "[1, 2, 3]"),
        (ReprSerializer, {"a": 1, "b": 2}, "{'a': 1, 'b': 2}"),
        (ReprSerializer, None, "None"),
        (
            ReprSerializer,
            datetime(2000, 1, 1, tzinfo=None),  # noqa: DTZ001
            "datetime.datetime(2000, 1, 1, 0, 0)",
        ),
        (
            ReprSerializer,
            datetime(2000, 1, 1),  # noqa: DTZ001
            "datetime.datetime(2000, 1, 1, 0, 0)",
        ),
        (
            ReprSerializer,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
            "datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)",
        ),
    ],
)
def test_basic_serializers(serializer_class: type[Serializer], value: Any, expected: str) -> None:
    """Test that serializers correctly convert values to strings."""
    assert serializer_class.serialize(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        123,  # Integer
        123.45,  # Float
        "hello",  # String
        (1, 2, 3),  # Tuple
    ],
)
def test_std_hash_key_serializer(value: Any) -> None:
    """Test StdHashSerializer correctly converts hashable values to hash strings."""
    hash_value = StdHashSerializer.serialize(value)

    # Check that the result is a string
    assert isinstance(hash_value, str)

    # Check that the result is a valid integer string (possibly negative)
    assert hash_value.isdigit() or (hash_value.startswith("-") and hash_value[1:].isdigit())

    # Test that same input produces same hash within the same session
    assert StdHashSerializer.serialize(value) == StdHashSerializer.serialize(value)


@pytest.mark.parametrize(
    "unhashable_value",
    [
        [1, 2, 3],  # Lists are unhashable
        {"a": 1, "b": 2},  # Dicts are unhashable
    ],
)
def test_std_hash_key_serializer_unhashable(unhashable_value: Any) -> None:
    """Test StdHashSerializer raises TypeError for unhashable types."""
    with pytest.raises(TypeError, match="unhashable type"):
        StdHashSerializer.serialize(unhashable_value)


def test_md5_key_serializer() -> None:
    """Test Md5Serializer correctly converts values to MD5 hash strings."""
    value = 123  # Example value to hash
    mock_hexdigest = Mock(return_value="a" * 32)
    mock_md5 = Mock()
    mock_md5.hexdigest = mock_hexdigest

    with patch("hashlib.md5", return_value=mock_md5) as mock_md5_func:
        result = Md5Serializer.serialize(value)

        # Verify md5 was called with string representation of value
        mock_md5_func.assert_called_once_with(str(value).encode(), usedforsecurity=False)
        # Verify hexdigest was called
        mock_hexdigest.assert_called_once()
        # Verify the result matches our mock
        assert result == "a" * 32


def test_key_serializer_cannot_be_instantiated() -> None:
    """Test that Serializer cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class Serializer"):
        Serializer()  # Abstract class cannot be instantiated
