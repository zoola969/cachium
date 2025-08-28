from __future__ import annotations

import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Any

import pytest

from cachium.storages import BaseLock, BaseStorage, Result
from cachium.storages.ttl_map import (
    AsyncLockStorage,
    LockStorage,
    SimpleAsyncLock,
    SimpleLock,
    TTLMapAsyncStorage,
    TTLMapStorage,
)

if TYPE_CHECKING:
    from concurrent.futures import Future


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
    lock_storage = LockStorage()
    key = "test_lock_key"
    lock = SimpleLock(lock_storage, key, timeout=None)

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


async def test__simple_lock_async() -> None:
    """Test SimpleLock in asynchronous context."""
    async_lock_storage = AsyncLockStorage()
    key = "test_lock_key"
    lock = SimpleAsyncLock(async_lock_storage, key, timeout=None)

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


def test__simple_lock__sync__concurrent_access() -> None:
    """Test SimpleLock in synchronous context with concurrent access."""
    lock_storage = LockStorage()
    result = Queue()

    shared_resource = {
        0.1: 1,
        0.01: 1,
    }

    def access_shared_resource(key: float) -> None:
        nonlocal shared_resource
        lock = SimpleLock(lock_storage, str(key), timeout=None)
        with lock:
            val = shared_resource[key]
            time.sleep(key)  # Simulate some work
            shared_resource[key] = val + 1
            result.put(key)

    # Create a thread pool executor to run tasks concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures: list[Future[None]] = [
            executor.submit(access_shared_resource, 0.1),
            executor.submit(access_shared_resource, 0.1),
            executor.submit(access_shared_resource, 0.01),
            executor.submit(access_shared_resource, 0.01),
        ]
        # Wait for completion
        for future in futures:
            future.result()

    # we can see that waiting for key 0.1 does not block waiting for key 0.01
    assert [result.get() for _ in range(4)] == [0.01, 0.01, 0.1, 0.1], "Concurrent access did not work as expected"
    # we can see that lock per key is acquired correctly
    assert list(shared_resource.values()) == [3, 3], "Shared resource was not updated correctly"


async def test__simple_lock__async__concurrent_access() -> None:
    """Test SimpleLock in asynchronous context with concurrent access."""
    lock_storage = AsyncLockStorage()
    result = asyncio.Queue()

    shared_resource = {
        0.1: 1,
        0.01: 1,
    }

    async def access_shared_resource(key: float) -> None:
        nonlocal shared_resource
        lock = SimpleAsyncLock(lock_storage, str(key), timeout=None)
        async with lock:
            val = shared_resource[key]
            await asyncio.sleep(key)  # Simulate some work
            shared_resource[key] = val + 1
            await result.put(key)

    # Create a thread pool executor to run tasks concurrently
    tasks = [
        access_shared_resource(0.1),
        access_shared_resource(0.1),
        access_shared_resource(0.01),
        access_shared_resource(0.01),
    ]
    if sys.version_info >= (3, 11):
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                tg.create_task(task)
    else:
        await asyncio.gather(*tasks)

    # we can see that waiting for key 0.1 does not block waiting for key 0.01
    assert [result.get_nowait() for _ in range(4)] == [
        0.01,
        0.01,
        0.1,
        0.1,
    ], "Concurrent access did not work as expected"
    # we can see that lock per key is acquired correctly
    assert list(shared_resource.values()) == [3, 3], "Shared resource was not updated correctly"


def test__ttl_map_storage__basic() -> None:
    storage = TTLMapStorage()
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


async def test__ttl_map_async_storage__basic() -> None:
    storage = TTLMapAsyncStorage()

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


def test__simple_lock__timeout():
    ls = LockStorage()
    timeout = 0.05
    res = Queue()

    def func(key: str, sleep_time: float, id_: int) -> None:
        ls.register_lock(key, id_, timeout=timeout)
        time.sleep(sleep_time)
        ls.unregister_lock(key, id_)
        res.put(id_)

    # Without timeout, the second thread would wait the first thread to finish and release the lock
    # But with timeout, it waits only for the specified time
    # force reacquires the lock and finishes before the first thread
    t1 = Thread(None, func, args=("test_key", 0.1, 1))
    t2 = Thread(None, func, args=("test_key", 0.01, 2))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert [res.get() for _ in range(2)] == [2, 1], "Timeout did not work as expected"


async def test__simple_async_lock__timeout():
    ls = AsyncLockStorage()
    timeout = 0.05
    res = asyncio.Queue()

    async def func(key: str, sleep_time: float, id_: int) -> None:
        await ls.register_lock(key, id_, timeout=timeout)
        await asyncio.sleep(sleep_time)
        await ls.unregister_lock(key, id_)
        await res.put(id_)

    # Without timeout, the second coro would wait the first one to finish and release the lock
    # But with timeout, it waits only for the specified time
    # force reacquires the lock and finishes before the first coro
    if sys.version_info >= (3, 11):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(func("test_key", 0.1, 1))
            tg.create_task(func("test_key", 0.01, 2))
    else:
        await asyncio.gather(
            func("test_key", 0.1, 1),
            func("test_key", 0.01, 2),
        )
    assert [res.get_nowait() for _ in range(2)] == [2, 1], "Timeout did not work as expected"
