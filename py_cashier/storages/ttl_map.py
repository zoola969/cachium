from __future__ import annotations

from asyncio import Condition as AsyncCondition
from datetime import timedelta
from threading import Condition
from typing import TYPE_CHECKING

from ttlru_map import TTLMap
from typing_extensions import override

from py_cashier.logger import logger

from ._abc import BaseAsyncLock, BaseAsyncStorage, BaseLock, BaseStorage, Result, TValue

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


__all__ = [
    "TTLMapAsyncStorage",
    "TTLMapStorage",
]


class LockStorage:
    def __init__(self) -> None:
        self._locks: set[str] = set()
        self._condition = Condition()

    def register_lock(self, key: str) -> None:
        with self._condition:
            while key in self._locks:
                logger.debug("Key '%s' is in use, waiting for release.", key)
                self._condition.wait()
            logger.debug("Registering lock for key '%s'.", key)
            self._locks.add(key)
            self._condition.notify_all()

    def unregister_lock(self, key: str) -> None:
        with self._condition:
            self._locks.discard(key)
            logger.debug("Unregistering lock for key '%s'.", key)
            self._condition.notify_all()


class AsyncLockStorage:
    def __init__(self) -> None:
        self._locks: set[str] = set()
        self._condition = AsyncCondition()

    async def register_lock(self, key: str) -> None:
        async with self._condition:
            while key in self._locks:
                logger.debug("Key '%s' is in use, waiting for release.", key)
                await self._condition.wait()
            logger.debug("Registering lock for key '%s'.", key)
            self._locks.add(key)
            self._condition.notify_all()

    async def unregister_lock(self, key: str) -> None:
        async with self._condition:
            self._locks.discard(key)
            logger.debug("Unregistering lock for key '%s'.", key)
            self._condition.notify_all()


class SimpleLock(BaseLock):
    def __init__(self, lock_storage: LockStorage, key: str) -> None:
        self._lock_storage = lock_storage
        self._key = key

    @override
    def __enter__(self) -> Self:
        self._lock_storage.register_lock(self._key)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._lock_storage.unregister_lock(self._key)


class SimpleAsyncLock(BaseAsyncLock):
    def __init__(self, lock_storage: AsyncLockStorage, key: str) -> None:
        self._lock_storage = lock_storage
        self._key = key

    @override
    async def __aenter__(self) -> Self:
        await self._lock_storage.register_lock(self._key)
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._lock_storage.unregister_lock(self._key)


class TTLMapStorage(BaseStorage[TValue, SimpleLock]):
    """In-memory storage with TTL and size limit."""

    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock_storage = LockStorage()
        self._storage: TTLMap[str, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @override
    def lock(self, key: str) -> SimpleLock:
        return SimpleLock(self._lock_storage, key)

    @override
    def get(self, key: str) -> Result[TValue] | None:
        try:
            return Result(self._storage[key])
        except KeyError:
            return None

    @override
    def set(self, key: str, value: TValue) -> None:
        self._storage[key] = value


class TTLMapAsyncStorage(BaseAsyncStorage[TValue, SimpleAsyncLock]):
    """Asynchronous in-memory storage with TTL and size limit."""

    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock_storage = AsyncLockStorage()
        self._storage: TTLMap[str, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @override
    def lock(self, key: str) -> SimpleAsyncLock:
        return SimpleAsyncLock(self._lock_storage, key)

    @override
    async def aget(self, key: str) -> Result[TValue] | None:
        try:
            return Result(self._storage[key])
        except KeyError:
            return None

    @override
    async def aset(self, key: str, value: TValue) -> None:
        self._storage[key] = value
