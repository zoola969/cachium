from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, patch

import pytest

from py_cashier import KeySerializer, Md5KeySerializer, ReprKeySerializer, StdHashKeySerializer, StrKeySerializer


@pytest.mark.parametrize(
    ("serializer_class", "value", "expected"),
    [
        # StrKeySerializer tests
        (StrKeySerializer, 123, "123"),
        (StrKeySerializer, 123.45, "123.45"),
        (StrKeySerializer, "hello", "hello"),
        (StrKeySerializer, [1, 2, 3], "[1, 2, 3]"),
        (StrKeySerializer, {"a": 1, "b": 2}, "{'a': 1, 'b': 2}"),
        (StrKeySerializer, None, "None"),
        (
            StrKeySerializer,
            datetime(2000, 1, 1, tzinfo=None),  # noqa: DTZ001
            "2000-01-01 00:00:00",
        ),
        (
            StrKeySerializer,
            datetime(2000, 1, 1),  # noqa: DTZ001
            "2000-01-01 00:00:00",
        ),
        (
            StrKeySerializer,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
            "2000-01-01 00:00:00+00:00",
        ),
        # ReprKeySerializer tests
        (ReprKeySerializer, 123, "123"),
        (ReprKeySerializer, 123.45, "123.45"),
        (ReprKeySerializer, "hello", "'hello'"),  # Note the quotes
        (ReprKeySerializer, [1, 2, 3], "[1, 2, 3]"),
        (ReprKeySerializer, {"a": 1, "b": 2}, "{'a': 1, 'b': 2}"),
        (ReprKeySerializer, None, "None"),
        (
            ReprKeySerializer,
            datetime(2000, 1, 1, tzinfo=None),  # noqa: DTZ001
            "datetime.datetime(2000, 1, 1, 0, 0)",
        ),
        (
            ReprKeySerializer,
            datetime(2000, 1, 1),  # noqa: DTZ001
            "datetime.datetime(2000, 1, 1, 0, 0)",
        ),
        (
            ReprKeySerializer,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
            "datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)",
        ),
    ],
)
def test_basic_serializers(serializer_class: type[KeySerializer], value: Any, expected: str) -> None:
    """Test that serializers correctly convert values to strings."""
    assert serializer_class.to_str(value) == expected


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
    """Test StdHashKeySerializer correctly converts hashable values to hash strings."""
    hash_value = StdHashKeySerializer.to_str(value)

    # Check that the result is a string
    assert isinstance(hash_value, str)

    # Check that the result is a valid integer string (possibly negative)
    assert hash_value.isdigit() or (hash_value.startswith("-") and hash_value[1:].isdigit())

    # Test that same input produces same hash within the same session
    assert StdHashKeySerializer.to_str(value) == StdHashKeySerializer.to_str(value)


@pytest.mark.parametrize(
    "unhashable_value",
    [
        [1, 2, 3],  # Lists are unhashable
        {"a": 1, "b": 2},  # Dicts are unhashable
    ],
)
def test_std_hash_key_serializer_unhashable(unhashable_value: Any) -> None:
    """Test StdHashKeySerializer raises TypeError for unhashable types."""
    with pytest.raises(TypeError, match="unhashable type"):
        StdHashKeySerializer.to_str(unhashable_value)


def test_md5_key_serializer() -> None:
    """Test Md5KeySerializer correctly converts values to MD5 hash strings."""
    value = 123  # Example value to hash
    mock_hexdigest = Mock(return_value="a" * 32)
    mock_md5 = Mock()
    mock_md5.hexdigest = mock_hexdigest

    with patch("hashlib.md5", return_value=mock_md5) as mock_md5_func:
        result = Md5KeySerializer.to_str(value)

        # Verify md5 was called with string representation of value
        mock_md5_func.assert_called_once_with(str(value).encode(), usedforsecurity=False)
        # Verify hexdigest was called
        mock_hexdigest.assert_called_once()
        # Verify the result matches our mock
        assert result == "a" * 32


def test_key_serializer_cannot_be_instantiated() -> None:
    """Test that KeySerializer cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class KeySerializer"):
        KeySerializer()  # Abstract class cannot be instantiated
