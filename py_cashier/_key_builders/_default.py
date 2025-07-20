from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import override

from py_cashier import ReprKeySerializer
from py_cashier._utils import NOT_SET, build_cache_key_template, collect_args_info

from ._abc import KeyBuilder

if TYPE_CHECKING:
    from py_cashier import KeySerializer

    from ._abc import TCacheKey


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
        func: Callable[..., Any],
        key_serializer: type[KeySerializer] = ReprKeySerializer,
        delimiter: str = "\t",
    ) -> None:
        """:param prefix: A string to be used as a prefix for keys.

        :type prefix: str
        :param func: The function whose arguments will be analyzed for cache generation purposes.
        :type func: Callable[..., Any]
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
    ) -> TCacheKey:
        call_args = self._get_call_args(*args, **kwargs)

        return f"{self._prefix}:{self._cache_key_template.format(**call_args)}"
