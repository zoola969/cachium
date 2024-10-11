from __future__ import annotations

from asyncio import iscoroutinefunction
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast, overload

from typing_extensions import ParamSpec

from py_cashier._builders import DefaultKeyBuilder
from py_cashier._storages import BaseLock, Result, TTLMapStorage
from py_cashier.logger import logger

if TYPE_CHECKING:
    from py_cashier._builders import KeyBuilder
    from py_cashier._storages import BaseStorage

TLock = TypeVar("TLock", bound=BaseLock)
P = ParamSpec("P")
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@overload
def cache(
    *,
    storage_class: type[BaseStorage[T, TLock]] | None = None,
    key_builder: KeyBuilder | None = None,
    max_size: int | None = 1024,
    ttl: timedelta | None = timedelta(minutes=1),
) -> Callable[[F], F]: ...


@overload
def cache(func: F, /) -> F: ...


def cache(
    func: F | None = None,
    /,
    *,
    storage_class: type[BaseStorage[T, TLock]] | None = None,
    key_builder: KeyBuilder | None = None,
    max_size: int | None = 1024,
    ttl: timedelta | None = timedelta(minutes=1),
) -> Callable[[F], F]:
    """Cache decorator."""
    if storage_class is None:
        storage_class = TTLMapStorage[T]

    def _decorator(func_: F) -> F:
        if iscoroutinefunction(func_):
            return cast("F", _async_wrapper(func_, storage_class, key_builder, max_size, ttl))
        return cast("F", _wrapper(func_, storage_class, key_builder, max_size, ttl))

    if func is None:
        return _decorator
    return _decorator(func)


def _wrapper(
    func: Callable[P, T],
    storage_class: type[BaseStorage[T, TLock]] | None,
    key_builder: KeyBuilder | None,
    max_size: int | None,
    ttl: timedelta | None,
) -> Callable[P, T]:
    if key_builder is None:
        key_builder = DefaultKeyBuilder(func=func)

    cache_storage = storage_class(max_size=max_size, ttl=ttl)

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = key_builder.build_key(*args, **kwargs)
        with cache_storage.lock(key):
            if (cached_result := cache_storage.get(key)) and isinstance(cached_result, Result):
                logger.debug("Value for key '%s' has been retrieved from cache", key)
                return cached_result.value
            logger.debug("No entry for key '%s' in cache", key)

            result = func(*args, **kwargs)

            cache_storage.set(key, result)
            logger.debug("Value for key '%s' has been set to cache", key)
        return result

    return wrapper


def _async_wrapper(
    func: Callable[P, T],
    storage_class: type[BaseStorage],
    key_builder: KeyBuilder | None,
    max_size: int | None = 1024,
    ttl: timedelta | None = timedelta(minutes=1),
) -> Callable[P, T]:
    if key_builder is None:
        key_builder = DefaultKeyBuilder(func=func)

    cache_storage = storage_class(max_size=max_size, ttl=ttl)

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = key_builder.build_key(*args, **kwargs)
        async with cache_storage.lock(key):
            if (cached_result := await cache_storage.aget(key)) and isinstance(cached_result, Result):
                logger.debug("Value for key '%s' has been retrieved from cache", key)
                return cached_result.value
            logger.debug("No entry for key '%s' in cache", key)

            result = await func(*args, **kwargs)

            await cache_storage.aset(key, result)
            logger.debug("Value for key '%s' has been set to cache", key)
        return result

    return wrapper
