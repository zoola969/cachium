from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, TypeVar, final, get_args, get_type_hints

from typing_extensions import ParamSpec

from cachium._errors import NoKwargsError

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

P = ParamSpec("P")
T = TypeVar("T")


@final
class NotSet: ...


NOT_SET = NotSet()


class ArgInfo(NamedTuple):
    position: int
    name: str
    cached: bool
    default: Any | NotSet


class FuncArgsInfo(NamedTuple):
    by_name: Mapping[str, ArgInfo]
    by_position: Sequence[str]
    args_name: str | None
    kwargs_name: str | None


class CacheWith:
    """Class to mark an argument as cacheable."""


def get_arg_default_value(argspec: inspect.FullArgSpec, arg_position: int) -> Any | NotSet:  # noqa: ANN401
    """Return the default value for an argument at a given position."""
    if argspec.defaults is None:
        return NOT_SET
    # the argument is keyword-only
    if arg_position >= len(argspec.args):
        return NOT_SET
    offset = len(argspec.args) - len(argspec.defaults)
    if arg_position < offset:
        return NOT_SET
    return argspec.defaults[arg_position - offset]


def get_kwarg_default_value(argspec: inspect.FullArgSpec, kwarg_name: str) -> Any | NotSet:  # noqa: ANN401
    """Return the default value for a keyword-only argument."""
    if kwarg_name not in argspec.kwonlyargs:
        raise NoKwargsError
    if not argspec.kwonlydefaults:
        return NOT_SET
    return argspec.kwonlydefaults.get(kwarg_name, NOT_SET)


def build_cache_key_template(sorted_arg_names: Iterable[str], *, delimiter: str = "\t") -> str:
    return delimiter.join(f"{arg_name}={{{arg_name}}}" for arg_name in sorted_arg_names)


def cached(type_alias: Any) -> bool:  # noqa: ANN401
    if type_alias is None:
        return False
    return any(isinstance(type_arg, CacheWith) or type_arg is CacheWith for type_arg in get_args(type_alias))


def collect_args_info(f: Callable[P, T]) -> FuncArgsInfo:
    argspec = inspect.getfullargspec(f)
    typing_info = get_type_hints(f, include_extras=True)
    by_name = {}
    by_position: list[str] = []
    for j, arg in enumerate(argspec.args):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=get_arg_default_value(argspec, j),
            cached=cached(typing_info.get(arg)),
        )
        by_position.append(arg)

    for j, arg in enumerate(argspec.kwonlyargs, start=len(argspec.args)):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=get_kwarg_default_value(argspec, arg),
            cached=cached(typing_info.get(arg)),
        )
    return FuncArgsInfo(by_name=by_name, by_position=by_position, args_name=argspec.varargs, kwargs_name=argspec.varkw)


def get_call_args(
    by_name: Mapping[str, ArgInfo],
    by_position: Sequence[str],
    args: Iterable[Any],
    kwargs: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Return mapping of argument names to their given values."""
    max_arg_number = len(by_position)
    for kw_name in kwargs:
        if (data := by_name.get(kw_name)) and (pos := data.position) is not None:
            max_arg_number = min(max_arg_number, pos)
    res = {}

    for i, arg_value in enumerate(args):
        arg_name = by_position[i]
        res[arg_name] = arg_value

    res.update((kw_name, kw_value) for kw_name, kw_value in kwargs.items() if kw_name in by_name)

    for name, info in by_name.items():
        if name in res:
            continue
        # Possible only if the function was called without one of the arguments
        if info.default is NOT_SET:  # pragma: no cover
            msg = f"Default value for argument '{name}' is not set"
            raise RuntimeError(msg)
        res[name] = info.default
    return res
