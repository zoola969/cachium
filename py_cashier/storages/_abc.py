from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from datetime import timedelta
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
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


class BaseAsyncLock(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


TLock = TypeVar("TLock", bound=BaseLock)
TAsyncLock = TypeVar("TAsyncLock", bound=BaseAsyncLock)


class BaseStorage(ABC, Generic[TValue, TLock]):
    @abstractmethod
    def lock(self, key: str, *, timeout: timedelta | None = None) -> TLock:
        """Return lock for the key."""

    @abstractmethod
    def get(self, key: str) -> Result[TValue] | None:
        """Get value by key."""

    @abstractmethod
    def set(self, key: str, value: TValue) -> None:
        """Set value by key."""


class BaseAsyncStorage(ABC, Generic[TValue, TAsyncLock]):
    @abstractmethod
    def lock(self, key: str, *, timeout: timedelta | None = None) -> TAsyncLock:
        """Return lock for the key."""

    @abstractmethod
    async def aget(self, key: str) -> Result[TValue] | None:
        """Get value by key async."""

    @abstractmethod
    async def aset(self, key: str, value: TValue) -> None:
        """Set value by key async."""
