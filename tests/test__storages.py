from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import Any

import pytest

from py_cashier._storages import BaseLock, BaseStorage, Result, SimpleLock, TTLMapStorage


@pytest.mark.parametrize(
    "value",
    [
        123,
        "hello",
        [1, 2, 3],
        {"a": 1, "b": 2},
        None,
    ],
)
def test_result_value(value: Any) -> None:
    """Test that Result wrapper correctly stores and returns values."""
    result = Result(value)
    assert result.value == value


@pytest.mark.parametrize(
    ("value", "expected_repr"),
    [
        (123, "Result(123)"),
        ("hello", "Result('hello')"),
        ([1, 2, 3], "Result([1, 2, 3])"),
    ],
)
def test_result_repr(value: Any, expected_repr: str) -> None:
    """Test the string representation of Result objects."""
    result = Result(value)
    assert repr(result) == expected_repr


def test_simple_lock_sync() -> None:
    """Test SimpleLock in synchronous context."""
    lock = SimpleLock()

    # Test that lock can be acquired and released
    with lock:
        # Lock is acquired here
        pass
    # Lock is released here

    # Test that lock prevents concurrent access
    shared_resource = 0

    def increment_shared_resource() -> None:
        nonlocal shared_resource
        with lock:
            # Simulate some work
            local_copy = shared_resource
            time.sleep(0.01)  # Small delay to simulate work
            shared_resource = local_copy + 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(increment_shared_resource) for _ in range(10)]
        for future in futures:
            future.result()  # Wait for completion

    # If the lock works correctly, each thread should increment by 1
    assert shared_resource == 10


async def test_simple_lock_async() -> None:
    """Test SimpleLock in asynchronous context."""
    lock = SimpleLock()

    # Test that lock can be acquired and released asynchronously
    async with lock:
        # Lock is acquired here
        pass
    # Lock is released here

    # Test that lock prevents concurrent access
    shared_resource = 0

    async def increment_shared_resource() -> None:
        nonlocal shared_resource
        async with lock:
            # Simulate some work
            local_copy = shared_resource
            await asyncio.sleep(0.01)  # Small delay to simulate work
            shared_resource = local_copy + 1

    # Create and gather tasks
    tasks = [increment_shared_resource() for _ in range(10)]
    await asyncio.gather(*tasks)

    # If the lock works correctly, each task should increment by 1
    assert shared_resource == 10


@pytest.mark.parametrize(
    "is_async",
    [False, True],
)
def test_ttl_map_storage_basic(is_async: bool) -> None:
    """Test TTLMapStorage basic functionality in both sync and async contexts."""
    # Create storage with default settings
    storage = TTLMapStorage()

    # Define test cases
    async def async_test() -> None:
        # Test set and get
        await storage.aset("key1", "value1")
        result = await storage.aget("key1")
        assert result is not None
        assert result.value == "value1"

        # Test get for non-existent key
        result = await storage.aget("non_existent_key")
        assert result is None

        # Test overwriting a key
        await storage.aset("key1", "new_value")
        result = await storage.aget("key1")
        assert result is not None
        assert result.value == "new_value"

    def sync_test() -> None:
        # Test set and get
        storage.set("key1", "value1")
        result = storage.get("key1")
        assert result is not None
        assert result.value == "value1"

        # Test get for non-existent key
        result = storage.get("non_existent_key")
        assert result is None

        # Test overwriting a key
        storage.set("key1", "new_value")
        result = storage.get("key1")
        assert result is not None
        assert result.value == "new_value"

    if is_async:
        asyncio.run(async_test())
    else:
        sync_test()


@pytest.mark.parametrize(
    ("ttl_ms", "sleep_ms", "should_expire"),
    [
        (100, 50, False),  # TTL not expired
        (100, 200, True),  # TTL expired
    ],
)
def test_ttl_map_storage_ttl(ttl_ms: int, sleep_ms: int, should_expire: bool) -> None:
    """Test TTLMapStorage time-to-live functionality with different TTL values."""
    # Create storage with the specified TTL
    storage = TTLMapStorage(ttl=timedelta(milliseconds=ttl_ms))

    # Set a value
    storage.set("key1", "value1")

    # Verify it's there
    result = storage.get("key1")
    assert result is not None
    assert result.value == "value1"

    # Wait for the specified time
    time.sleep(sleep_ms / 1000)  # Convert ms to seconds

    # Verify whether the value is still there or expired
    result = storage.get("key1")
    if should_expire:
        assert result is None
    else:
        assert result is not None
        assert result.value == "value1"


@pytest.mark.parametrize(
    ("max_size", "keys_to_add", "expected_max_keys"),
    [
        (2, ["key1", "key2", "key3", "key4"], 2),  # Small cache, should evict
        (4, ["key1", "key2", "key3"], 3),  # Larger cache, no eviction needed
    ],
)
def test_ttl_map_storage_max_size(max_size: int, keys_to_add: list[str], expected_max_keys: int) -> None:
    """Test TTLMapStorage max size functionality with different configurations."""
    # Create storage with the specified max size
    storage = TTLMapStorage(max_size=max_size, ttl=None)  # No TTL, just max size

    # Add all the keys
    for i, key in enumerate(keys_to_add):
        storage.set(key, f"value{i+1}")

    # Count the number of keys that are still in the cache
    keys_in_cache = 0
    for key in keys_to_add:
        if storage.get(key) is not None:
            keys_in_cache += 1

    # Verify we don't exceed the max size
    assert keys_in_cache <= max_size

    # If we added more keys than max_size, verify the most recently added key is in the cache
    if len(keys_to_add) > max_size:
        assert storage.get(keys_to_add[-1]) is not None


@pytest.mark.parametrize(
    ("max_size", "ttl"),
    [
        (10, timedelta(minutes=1)),
        (100, timedelta(seconds=30)),
        (5, None),
    ],
)
def test_ttl_map_storage_build(max_size: int, ttl: timedelta | None) -> None:
    """Test TTLMapStorage.build factory method with different configurations."""
    # Create a factory with the specified max_size
    factory = TTLMapStorage.build(max_size=max_size)

    # Create a storage with the specified TTL
    storage = factory(ttl=ttl)

    # Verify it's a TTLMapStorage instance
    assert isinstance(storage, TTLMapStorage)

    # Test basic functionality
    storage.set("key1", "value1")
    result = storage.get("key1")
    assert result is not None
    assert result.value == "value1"


@pytest.mark.parametrize(
    "key",
    ["key1", "another_key", ""],
)
def test_ttl_map_storage_lock(key: str) -> None:
    """Test TTLMapStorage lock method with different keys."""
    storage = TTLMapStorage()

    # Get a lock for the key
    lock = storage.lock(key)

    # Verify it's a SimpleLock instance
    assert isinstance(lock, SimpleLock)

    # Test that the lock works
    with lock:
        # Lock is acquired here
        pass
    # Lock is released here


@pytest.mark.parametrize(
    ("abstract_class", "error_message"),
    [
        (BaseStorage, "Can't instantiate abstract class BaseStorage"),
        (BaseLock, "Can't instantiate abstract class BaseLock"),
    ],
)
def test_abstract_classes_cannot_be_instantiated(abstract_class: type, error_message: str) -> None:
    """Test that abstract classes cannot be instantiated directly."""
    with pytest.raises(TypeError) as excinfo:
        abstract_class()  # Abstract class cannot be instantiated

    # Check that the error message contains the expected text
    assert error_message in str(excinfo.value)
