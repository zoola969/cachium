from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import timedelta
from functools import partial
from threading import Lock
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from ttlru_map import TTLMap
from typing_extensions import override

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

TValue = TypeVar("TValue")


class Result(Generic[TValue]):
    """Result wrapper."""

    __slots__ = ("_value",)

    def __init__(self, value: TValue) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Result({self._value!r})"

    @property
    def value(self) -> TValue:
        """Return the inner value."""
        return self._value


class BaseLock(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


TLock = TypeVar("TLock", bound=BaseLock)


class BaseStorage(ABC, Generic[TValue, TLock]):
    @abstractmethod
    def lock(self, key: str) -> TLock:
        """Return lock for the key."""

    @abstractmethod
    async def aget(self, key: str) -> Result[TValue] | None:
        """Get value by key async."""

    @abstractmethod
    async def aset(self, key: str, value: TValue) -> None:
        """Set value by key async."""

    @abstractmethod
    def get(self, key: str) -> Result[TValue] | None:
        """Get value by key."""

    @abstractmethod
    def set(self, key: str, value: TValue) -> None:
        """Set value by key."""


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
