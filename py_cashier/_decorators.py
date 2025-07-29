from __future__ import annotations

from asyncio import iscoroutinefunction
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, cast

from typing_extensions import ParamSpec

from py_cashier._key_builders import DefaultKeyBuilder
from py_cashier._storages import BaseAsyncLock, BaseAsyncStorage, BaseLock, BaseStorage, Result
from py_cashier.logger import logger

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from py_cashier._key_builders import KeyBuilder

TLock = TypeVar("TLock", bound=BaseLock)
TAsyncLock = TypeVar("TAsyncLock", bound=BaseAsyncLock)
P = ParamSpec("P")
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class PKeyBuilder(Protocol):
    def __call__(self) -> KeyBuilder: ...


class PStorage(Protocol[T, TLock]):
    def __call__(self) -> BaseStorage[T, TLock]: ...


class PAsyncStorage(Protocol[T, TAsyncLock]):
    def __call__(self) -> BaseAsyncStorage[T, TAsyncLock]: ...


def cache(
    *,
    storage: PStorage[T, TLock] | PAsyncStorage[T, TAsyncLock],
    key_builder: PKeyBuilder | None = None,
) -> Callable[[F], F]:
    """Cache decorator."""

    def _decorator(f: F) -> F:
        k = key_builder() if key_builder is not None else DefaultKeyBuilder(func=f)
        s = storage()
        if iscoroutinefunction(f):
            if not isinstance(s, BaseAsyncStorage):
                msg = "Async function requires an async storage"
                raise TypeError(msg)
            return cast(
                "F",
                _async_wrapper(func=f, storage=s, key_builder=k),
            )
        if not isinstance(s, BaseStorage):
            msg = "Regular function requires a sync storage"
            raise TypeError(msg)
        return cast(
            "F",
            _wrapper(func=f, storage=s, key_builder=k),
        )

    return _decorator


def _wrapper(
    func: Callable[P, T],
    storage: BaseStorage[T, TLock],
    key_builder: KeyBuilder,
) -> Callable[P, T]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = key_builder.build_key(*args, **kwargs)
        with storage.lock(key):
            if (cached_result := storage.get(key)) and isinstance(cached_result, Result):
                logger.debug("Value for key '%s' has been retrieved from cache", key)
                return cached_result.value
            logger.debug("No entry for key '%s' in cache", key)

            result = func(*args, **kwargs)

            storage.set(key, result)
            logger.debug("Value for key '%s' has been set to cache", key)
        return result

    return wrapper


def _async_wrapper(
    func: Callable[P, Awaitable[T]],
    storage: BaseAsyncStorage[T, TAsyncLock],
    key_builder: KeyBuilder,
) -> Callable[P, Awaitable[T]]:

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = key_builder.build_key(*args, **kwargs)
        async with storage.lock(key):
            if (cached_result := await storage.aget(key)) and isinstance(cached_result, Result):
                logger.debug("Value for key '%s' has been retrieved from cache", key)
                return cached_result.value
            logger.debug("No entry for key '%s' in cache", key)

            result = await func(*args, **kwargs)
            await storage.aset(key, result)
            logger.debug("Value for key '%s' has been set to cache", key)
        return result

    return wrapper
