import asyncio
import time
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta

from py_cashier import cache


def test__cache():
    calls: dict[tuple[int, int], int] = defaultdict(int)

    @cache
    def func(a: int, b: int) -> int:
        nonlocal calls
        calls[(a, b)] += 1
        return a + b

    # 1st attempt
    assert func(1, 2) == 3
    assert func(1, 2) == 3
    assert calls[(1, 2)] == 1

    # 2nd attempt
    assert func(1, 1) == 2
    assert func(1, 1) == 2
    assert calls[(1, 1)] == 1


async def test__cache__async():
    calls: dict[tuple[int, int], int] = defaultdict(int)

    @cache(ttl=timedelta(seconds=1))
    async def func(a: int, b: int) -> int:
        nonlocal calls
        calls[(a, b)] += 1
        return a + b

    # 1st attempt
    assert await func(1, 2) == 3
    assert await func(1, 2) == 3
    assert calls[(1, 2)] == 1

    # 2nd attempt
    assert await func(1, 1) == 2
    assert await func(1, 1) == 2
    assert calls[(1, 1)] == 1


async def test__cache__dog_piling__async():
    """Test dog-piling prevention in an asynchronous context.

    Tests the behavior of the caching mechanism to prevent dog-piling in an
    asynchronous context. It verifies that concurrent calls to a cached
    function with the same arguments at the same time result in only one actual function call,
    returning the cached result for the rest.

    """
    calls = 0

    @cache(ttl=timedelta(seconds=1))
    async def func(a: int, b: int) -> int:
        await asyncio.sleep(0.1)
        nonlocal calls
        calls += 1
        return a + b

    tasks = [func(1, 2) for _ in range(100)]

    results = await asyncio.gather(*tasks)
    assert all(result == 3 for result in results)
    assert calls == 1


def test__cache__dog_piling__sync():
    """Test that the cache decorator prevents dog-piling in a multithreaded environment.

    Dog-piling occurs when multiple threads try to compute the same value simultaneously.
    The cache should ensure the function is called only once despite multiple concurrent requests.
    """
    calls = 0

    @cache
    def func(a: int, b: int) -> int:
        time.sleep(0.1)
        nonlocal calls
        calls += 1
        return a + b

    # Configure concurrent environment
    workers_count = 16
    tasks_count = workers_count * 8
    executor = ThreadPoolExecutor(max_workers=workers_count)

    # Create input arguments - each call will pass a tuple of (1, 2)
    input_args = ((1, 2) for _ in range(tasks_count))

    # Execute a function concurrently and check results
    results = executor.map(lambda p: func(*p), input_args)

    # Verify all results equal 3, and the function was called exactly once
    assert all(result == 3 for result in results)
    assert calls == 1


def test__cache__failing_func__sync():
    calls = 0

    @cache
    def func(a: int, b: int) -> int:
        time.sleep(0.03)
        nonlocal calls
        calls += 1
        msg = f"Test error: {a}, {b}"
        raise ValueError(msg)

    workers_count = 16
    tasks_count = workers_count * 2
    executor = ThreadPoolExecutor(max_workers=workers_count)

    # Create input arguments - each call will pass a tuple of (1, 2)
    input_args = ((1, 2) for _ in range(tasks_count))

    # Execute a function concurrently and check results

    def func2(p: tuple[int, int]) -> int:
        try:
            return func(*p)
        except ValueError:
            return 0

    results = executor.map(func2, input_args)

    assert all(result == 0 for result in results)
    assert calls == tasks_count


async def test__cache__failing_func__async():
    calls = 0

    @cache(ttl=timedelta(seconds=1))
    async def func(a: int, b: int) -> int:
        await asyncio.sleep(0.1)
        nonlocal calls
        calls += 1
        msg = f"Test error: {a}, {b}"
        raise ValueError(msg)

    async def func2(a: int, b: int) -> int:
        try:
            return await func(a, b)
        except ValueError:
            return 0

    tasks_count = 10
    tasks = [func2(1, 2) for _ in range(tasks_count)]

    results = await asyncio.gather(*tasks)

    assert all(result == 0 for result in results)
    assert calls == tasks_count
