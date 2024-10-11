from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import override

from py_cashier._serializers import ReprKeySerializer
from py_cashier._utils import NOT_SET, build_cache_key_template, collect_args_info

if TYPE_CHECKING:
    from py_cashier._serializers import CacheKey, KeySerializer


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
    ) -> CacheKey:
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


class DefaultKeyBuilder(KeyBuilder):
    """DefaultKeyBuilder is a subclass of KeyBuilder designed for constructing cache keys.

    This class generates cache keys based on a given function signature and dynamically provided
    arguments. It uses an optional prefix, a delimiter for separating elements in the key, and a
    key serialization strategy. DefaultKeyBuilder facilitates efficient and unique cache key
    generation for caching systems by utilizing detailed argument inspection.
    """

    def __init__(
        self,
        *,
        prefix: str | None = None,
        func: Callable[[...], Any],
        key_serializer: type[KeySerializer] = ReprKeySerializer,
        delimiter: str = "\t",
    ) -> None:
        """:param prefix: A string to be used as a prefix for keys.

        :type prefix: str
        :param func: The function whose arguments will be analyzed for cache generation purposes.
        :type func: Callable[[...], Any]
        :param key_serializer: A serializer class used to serialize the cache keys.
        :type key_serializer: type[KeySerializer]
        :param delimiter:  A delimiter string used for separating key-value pairs in the generated cache key.
        :type delimiter: str
        :returns: None
        :rtype: None
        """
        self._key_serializer = key_serializer
        self._prefix = self._build_key_prefix(func, prefix)
        self._by_name, self._by_position, self._args_name, self._kwargs_name = collect_args_info(func)
        self._cache_by_args = tuple(arg_name for arg_name, arg_info in self._by_name.items() if arg_info.cached)
        self._cache_key_template = build_cache_key_template(
            (
                arg_name
                for arg_name, arg_info in sorted(
                    self._by_name.items(),
                    key=lambda item: item[1].position,
                )
                if not self._cache_by_args or arg_name in self._cache_by_args
            ),
            delimiter=delimiter,
        )

    def _build_key_prefix(self, func: Callable[..., Any], prefix: str | None) -> str:
        """Build the prefix for the cache key."""
        if not prefix:
            return f"{inspect.getfile(func)}:{func.__name__}"
        return f"{prefix}:{inspect.getfile(func)}:{func.__name__}"

    def _get_call_args(self, *args: Any, **kwargs: Any) -> dict[str, str]:  # noqa: ANN401
        """Return mapping of argument names to their given values."""
        max_arg_number = len(self._by_position)
        for kw_name in kwargs:
            if (data := self._by_name.get(kw_name)) and (pos := data.position) is not None:
                max_arg_number = min(max_arg_number, pos)
        res = {}

        for i, arg_value in enumerate(args):
            arg_name = self._by_position[i]
            if not self._cache_by_args or arg_name in self._cache_by_args:
                res[arg_name] = self._key_serializer.to_str(arg_value)

        for kw_name, kw_value in kwargs.items():
            if kw_name in self._by_name and (not self._cache_by_args or kw_name in self._cache_by_args):
                res[kw_name] = self._key_serializer.to_str(kw_value)

        for name, info in self._by_name.items():
            if name in res or (self._cache_by_args and name not in self._cache_by_args):
                continue
            if info.default is NOT_SET:
                msg = f"Default value for argument '{name}' is not set"
                raise RuntimeError(msg)
            res[name] = self._key_serializer.to_str(info.default)
        return res

    @override
    def build_key(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> CacheKey:
        call_args = self._get_call_args(*args, **kwargs)

        return f"{self._prefix}:{self._cache_key_template.format(**call_args)}"
