from __future__ import annotations

from datetime import timedelta
from functools import partial
from threading import Condition
from typing import TYPE_CHECKING, Callable

from ttlru_map import TTLMap
from typing_extensions import override

from py_cashier.logger import logger

from ._abc import BaseLock, BaseStorage, Result, TValue

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


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

    # Async context manager methods are useless here, as the lock logic is synchronous.
    @override
    async def __aenter__(self) -> Self:
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._lock_storage.unregister_lock(self._key)


class TTLMapStorage(BaseStorage[TValue, SimpleLock]):
    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock_storage = LockStorage()
        self._storage: TTLMap[str, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @classmethod
    def build(cls, max_size: int | None = 1024) -> Callable[[timedelta | None], Self]:
        return partial(cls, max_size=max_size)

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

    @override
    async def aget(self, key: str) -> Result[TValue] | None:
        return self.get(key)

    @override
    async def aset(self, key: str, value: TValue) -> None:
        return self.set(key, value)
