from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

TCacheKey: TypeAlias = str


class KeyBuilder(ABC):
    """A generic abstract base class for building cache keys.

    This class serves as a blueprint for creating cache keys based on
    custom logic defined in subclasses. It provides an interface that
    enforces implementation of the 'build_key' method, which must be
    overridden to define specific key-building behavior. This helps in
    ensuring consistent and reusable caching mechanisms.
    """

    @abstractmethod
    def build_key(
        self,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> TCacheKey:
        """Abstract method for building a cache key.

            This method must be implemented by subclasses to define the mechanism
            for constructing a unique key for caching purposes, using the provided
            arguments and keyword arguments. The implementation of this method must
            return a value of the type `CacheKey`, which serves as the identifier for
            cached data.

        :param args: Positional arguments of the function call.
        :type args: Any
        :param kwargs: Keyword arguments of the function call.
        :type kwargs: Any
        :returns: A unique key representing the cache entry.
        :rtype: CacheKey

        """
