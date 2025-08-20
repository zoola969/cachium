from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import override

from cachium._helpers import build_cache_key_template, collect_args_info, get_call_args
from cachium.serializers import ReprSerializer

from ._abc import KeyBuilder

if TYPE_CHECKING:
    from cachium.serializers import Serializer

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
        key_serializer: type[Serializer] = ReprSerializer,
        delimiter: str = "\t",
    ) -> None:
        """:param prefix: A string to be used as a prefix for keys.

        :type prefix: str
        :param func: The function whose arguments will be analyzed for cache generation purposes.
        :type func: Callable[..., Any]
        :param key_serializer: A serializer class used to serialize the cache keys.
        :type key_serializer: type[Serializer]
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

    @staticmethod
    def _build_key_prefix(func: Callable[..., Any], prefix: str | None) -> str:
        """Build the prefix for the cache key."""
        if not prefix:
            return f"{inspect.getfile(func)}:{func.__name__}"
        return f"{prefix}:{inspect.getfile(func)}:{func.__name__}"

    def _get_call_args(self, *args: Any, **kwargs: Any) -> dict[str, str]:  # noqa: ANN401
        """Return mapping of argument names to their given values."""
        call_args = get_call_args(self._by_name, self._by_position, args, kwargs)
        return {
            name: self._key_serializer.serialize(value)
            for name, value in call_args.items()
            if not self._cache_by_args or name in self._cache_by_args
        }

    @override
    def build_key(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TCacheKey:
        call_args = self._get_call_args(*args, **kwargs)

        return f"{self._prefix}:{self._cache_key_template.format(**call_args)}"
