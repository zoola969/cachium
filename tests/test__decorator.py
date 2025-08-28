from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta
from typing import TYPE_CHECKING, Annotated, Any

import pytest

from cachium import CacheWith, cache
from cachium.storages.ttl_map import TTLMapAsyncStorage, TTLMapStorage

if TYPE_CHECKING:
    from collections.abc import Callable

    from cachium._decorators import PAsyncStorage, PStorage


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (1, 1, 2),
        (5, 10, 15),
    ],
)
def test_cache(a: int, b: int, expected: int) -> None:
    """Test that the cache decorator works correctly for synchronous functions."""
    calls: dict[tuple[int, int], int] = defaultdict(int)

    @cache(storage=lambda: TTLMapStorage(max_size=1000, ttl=timedelta(seconds=1)))
    def func(x: int, y: int) -> int:
        nonlocal calls
        calls[(x, y)] += 1
        return x + y

    # First call should execute the function
    assert func(a, b) == expected

    # Second call should use the cached result
    assert func(a, b) == expected

    # The function should only be called once for each unique set of arguments
    assert calls[(a, b)] == 1


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (1, 1, 2),
        (5, 10, 15),
    ],
)
async def test_cache_async(a: int, b: int, expected: int) -> None:
    """Test that the cache decorator works correctly for asynchronous functions."""
    calls: dict[tuple[int, int], int] = defaultdict(int)

    @cache(storage=lambda: TTLMapAsyncStorage(max_size=1000, ttl=timedelta(seconds=1)))
    async def func(x: int, y: int) -> int:
        nonlocal calls
        calls[(x, y)] += 1
        return x + y

    # First call should execute the function
    assert await func(a, b) == expected

    # Second call should use the cached result
    assert await func(a, b) == expected

    # The function should only be called once for each unique set of arguments
    assert calls[(a, b)] == 1


@pytest.mark.parametrize(
    ("a", "b", "expected", "tasks_count"),
    [
        (1, 2, 3, 100),
        (5, 10, 15, 50),
    ],
)
async def test_cache_dog_piling_async(a: int, b: int, expected: int, tasks_count: int) -> None:
    """Test dog-piling prevention in an asynchronous context.

    Tests the behavior of the caching mechanism to prevent dog-piling in an
    asynchronous context. It verifies that concurrent calls to a cached
    function with the same arguments at the same time result in only one actual function call,
    returning the cached result for the rest.
    """
    calls = 0

    @cache(storage=lambda: TTLMapAsyncStorage(max_size=1000, ttl=timedelta(seconds=1)))
    async def func(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        nonlocal calls
        calls += 1
        return x + y

    tasks = [func(a, b) for _ in range(tasks_count)]

    results = await asyncio.gather(*tasks)
    assert all(result == expected for result in results)
    assert calls == 1


@pytest.mark.parametrize(
    ("a", "b", "expected", "workers_count"),
    [
        (1, 2, 3, 16),
        (5, 10, 15, 8),
    ],
)
def test_cache_dog_piling_sync(a: int, b: int, expected: int, workers_count: int) -> None:
    """Test that the cache decorator prevents dog-piling in a multithreaded environment.

    Dog-piling occurs when multiple threads try to compute the same value simultaneously.
    The cache should ensure the function is called only once despite multiple concurrent requests.
    """
    calls = 0

    @cache(storage=lambda: TTLMapStorage(max_size=1000, ttl=timedelta(seconds=1)))
    def func(x: int, y: int) -> int:
        time.sleep(0.1)
        nonlocal calls
        calls += 1
        return x + y

    # Configure concurrent environment
    tasks_count = workers_count * 8
    executor = ThreadPoolExecutor(max_workers=workers_count)

    # Create input arguments - each call will pass a tuple of (a, b)
    input_args = ((a, b) for _ in range(tasks_count))

    # Execute a function concurrently and check results
    results = executor.map(lambda p: func(*p), input_args)

    # Verify all results equal the expected value, and the function was called exactly once
    assert all(result == expected for result in results)
    assert calls == 1


@pytest.mark.parametrize(
    ("a", "b", "workers_count"),
    [
        (1, 2, 16),
        (5, 10, 8),
    ],
)
def test_cache_failing_func_sync(a: int, b: int, workers_count: int) -> None:
    """Test that failing functions are not cached in synchronous context."""
    calls = 0

    @cache(storage=lambda: TTLMapStorage(max_size=1000, ttl=timedelta(seconds=1)))
    def func(x: int, y: int) -> int:
        time.sleep(0.03)
        nonlocal calls
        calls += 1
        msg = f"Test error: {x}, {y}"
        raise ValueError(msg)

    tasks_count = workers_count * 2
    executor = ThreadPoolExecutor(max_workers=workers_count)

    # Create input arguments - each call will pass the same tuple
    input_args = ((a, b) for _ in range(tasks_count))

    # Execute a function concurrently and check results
    def func2(p: tuple[int, int]) -> int:
        try:
            return func(*p)
        except ValueError:
            return 0

    results = executor.map(func2, input_args)

    assert all(result == 0 for result in results)
    # Each call should execute the function (no caching of errors)
    assert calls == tasks_count


@pytest.mark.parametrize(
    ("a", "b", "tasks_count"),
    [
        (1, 2, 10),
        (5, 10, 5),
    ],
)
async def test_cache_failing_func_async(a: int, b: int, tasks_count: int) -> None:
    """Test that failing functions are not cached in asynchronous context."""
    calls = 0

    @cache(storage=lambda: TTLMapAsyncStorage(max_size=1000, ttl=timedelta(seconds=1)))
    async def func(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        nonlocal calls
        calls += 1
        msg = f"Test error: {x}, {y}"
        raise ValueError(msg)

    async def func2(x: int, y: int) -> int:
        try:
            return await func(x, y)
        except ValueError:
            return 0

    tasks = [func2(a, b) for _ in range(tasks_count)]

    results = await asyncio.gather(*tasks)

    assert all(result == 0 for result in results)
    # Each call should execute the function (no caching of errors)
    assert calls == tasks_count


async def _af() -> None:
    pass


def _f() -> None:
    pass


@pytest.mark.parametrize(
    ("func", "storage"),
    [
        (_af, lambda: TTLMapStorage(max_size=1000, ttl=timedelta(seconds=1))),
        (_f, lambda: TTLMapAsyncStorage(max_size=1000, ttl=timedelta(seconds=1))),
    ],
)
def test__decorator__invalid_storage(func: Callable[..., Any], storage: PStorage | PAsyncStorage) -> None:
    """Test that the decorator raises TypeError for invalid storage."""
    with pytest.raises(TypeError, match="(Async|Regular) function requires a(n async| sync) storage"):
        cache(storage=storage)(func)


def test__decorator__cache_only_by_chosen_args():
    calls: dict[tuple[str, int, float], int] = defaultdict(int)

    @cache(storage=lambda: TTLMapStorage(max_size=1000, ttl=timedelta(seconds=1)))
    def func(a: Annotated[str, CacheWith()], b: int, c: Annotated[float, CacheWith]) -> str:
        nonlocal calls
        calls[(a, b, c)] += 1
        return f"{a}, {c}"

    result = []
    result.append(func("test", 1, 1.0))
    result.append(func("test", 2, 1.0))  # this call hits the cache, despite different `b`
    result.append(func("test2", 1, 1.0))
    result.append(func("test", 1, 2.0))

    assert result == ["test, 1.0", "test, 1.0", "test2, 1.0", "test, 2.0"]
    assert all(v == 1 for v in calls.values())
