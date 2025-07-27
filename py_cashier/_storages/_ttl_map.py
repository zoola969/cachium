from __future__ import annotations

import asyncio
from datetime import timedelta
from functools import partial
from threading import Lock
from typing import TYPE_CHECKING, Callable

from ttlru_map import TTLMap
from typing_extensions import override

from ._abc import BaseLock, BaseStorage, Result, TValue

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


class SimpleLock(BaseLock):
    def __init__(self) -> None:
        self._lock = Lock()

    def __enter__(self) -> Self:
        self._lock.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._lock.release()

    async def __aenter__(self) -> Self:
        await asyncio.to_thread(self._lock.acquire)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return self.__exit__(exc_type, exc_val, exc_tb)


class TTLMapStorage(BaseStorage[TValue, SimpleLock]):
    def __init__(
        self,
        max_size: int | None = 1024,
        ttl: timedelta | None = timedelta(minutes=1),
    ) -> None:
        self._lock = SimpleLock()
        self._storage: TTLMap[str, TValue] = TTLMap(max_size=max_size, ttl=ttl)

    @classmethod
    def build(cls, max_size: int | None = 1024) -> Callable[[timedelta | None], Self]:
        return partial(cls, max_size=max_size)

    @override
    def lock(self, key: str) -> SimpleLock:
        return self._lock

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
