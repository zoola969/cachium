from __future__ import annotations

import asyncio
import sys
import time
from asyncio import Condition as AsyncCondition
from datetime import timedelta
from threading import Condition
from typing import TYPE_CHECKING

from ttlru_map import TTLMap
from typing_extensions import override

from cachium.logger import logger

from ._abc import BaseAsyncLock, BaseAsyncStorage, BaseLock, BaseStorage, Result, TValue

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    from cachium.key_builders import TCacheKey


if sys.version_info < (3, 11):
    TimeoutError_ = asyncio.TimeoutError
else:  # pragma: no cover
    TimeoutError_ = TimeoutError

__all__ = [
    "TTLMapAsyncStorage",
    "TTLMapStorage",
]


class LockStorage:
    def __init__(self) -> None:
        self._locks: dict[TCacheKey, int] = {}
        self._condition = Condition()

    def register_lock(self, key: TCacheKey, id_: int, timeout: float | None) -> None:
        deadline = time.monotonic() + timeout if timeout is not None else None
        with self._condition:

            while key in self._locks:
                logger.debug("Key '%s' is in use, waiting for release.", key)
                wait_time = deadline - time.monotonic() if deadline is not None else None
                if wait_time is not None and wait_time <= 0:
                    logger.debug("Timeout reached trying to register lock for key '%s'. Forcing acquisition.", key)
                    break
                self._condition.wait(wait_time)

            logger.debug("Registering lock for key '%s'.", key)
            self._locks[key] = id_
            self._condition.notify_all()

    def unregister_lock(self, key: TCacheKey, id_: int) -> None:
        with self._condition:
            if self._locks.get(key) == id_:
                del self._locks[key]
            logger.debug("Lock for key '%s' has been unregistered.", key)
            self._condition.notify_all()


class AsyncLockStorage:
    def __init__(self) -> None:
        self._locks: dict[TCacheKey, int] = {}
        self._condition = AsyncCondition()

    async def register_lock(self, key: TCacheKey, id_: int, timeout: float | None) -> None:
        async with self._condition:

            while key in self._locks:
                logger.debug("Key '%s' is in use, waiting for release.", key)
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=timeout)
                except TimeoutError_:
                    logger.debug("Timeout reached trying to register lock for key '%s'. Forcing acquisition.", key)
                    break

            logger.debug("Registering lock for key '%s'.", key)
            self._locks[key] = id_
            self._condition.notify_all()

    async def unregister_lock(self, key: TCacheKey, id_: int) -> None:
        async with self._condition:
            if self._locks.get(key) == id_:
                del self._locks[key]
            logger.debug("Lock for key '%s' has been unregistered.", key)
            self._condition.notify_all()


class SimpleLock(BaseLock):
    def __init__(self, lock_storage: LockStorage, key: TCacheKey, timeout: timedelta | None) -> None:
        self._id = id(self)
        self._lock_storage = lock_storage
        self._key = key
        self._timeout = timeout.total_seconds() if timeout is not None else None

    @override
    def __enter__(self) -> Self:
        self._lock_storage.register_lock(self._key, self._id, self._timeout)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._lock_storage.unregister_lock(self._key, self._id)


class SimpleAsyncLock(BaseAsyncLock):
    def __init__(self, lock_storage: AsyncLockStorage, key: TCacheKey, timeout: timedelta | None) -> None:
        self._id = id(self)
        self._lock_storage = lock_storage
        self._key = key
        self._timeout = timeout.total_seconds() if timeout is not None else None

    @override
    async def __aenter__(self) -> Self:
        await self._lock_storage.register_lock(self._key, self._id, self._timeout)
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._lock_storage.unregister_lock(self._key, self._id)


class TTLMapStorage(BaseStorage[TValue, SimpleLock]):
    """In-memory storage with TTL and size limit."""

    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock_storage = LockStorage()
        self._storage: TTLMap[TCacheKey, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @override
    def lock(self, key: TCacheKey, *, timeout: timedelta | None = None) -> SimpleLock:
        return SimpleLock(self._lock_storage, key, timeout)

    @override
    def get(self, key: TCacheKey) -> Result[TValue] | None:
        try:
            return Result(self._storage[key])
        except KeyError:
            return None

    @override
    def set(self, key: TCacheKey, value: TValue) -> None:
        self._storage[key] = value


class TTLMapAsyncStorage(BaseAsyncStorage[TValue, SimpleAsyncLock]):
    """Asynchronous in-memory storage with TTL and size limit."""

    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock_storage = AsyncLockStorage()
        self._storage: TTLMap[TCacheKey, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @override
    def lock(self, key: TCacheKey, *, timeout: timedelta | None = None) -> SimpleAsyncLock:
        return SimpleAsyncLock(self._lock_storage, key, timeout)

    @override
    async def aget(self, key: TCacheKey) -> Result[TValue] | None:
        try:
            return Result(self._storage[key])
        except KeyError:
            return None

    @override
    async def aset(self, key: TCacheKey, value: TValue) -> None:
        self._storage[key] = value
