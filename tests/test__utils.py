from typing import Annotated, Any, Callable

import pytest

from py_cashier import CacheWith
from py_cashier._utils import NOT_SET, ArgInfo, FuncArgsInfo, cached, collect_args_info, get_call_args
from tests.functions import TestFunctions


@pytest.mark.parametrize(
    ("type_alias", "expected"),
    [
        (None, False),
        (int, False),
        (Annotated[int, CacheWith()], True),
        (Annotated[int, Exception(), CacheWith()], True),
    ],
)
def test__cached(type_alias: Any, expected: bool) -> None:
    assert cached(type_alias) == expected


@pytest.mark.parametrize(
    ("func", "args_info"),
    [
        (
            lambda: None,
            FuncArgsInfo(by_name={}, by_position=[], args_name=None, kwargs_name=None),
        ),
        (
            lambda *args, **kwargs: None,
            FuncArgsInfo(
                by_name={},
                by_position=[],
                args_name="args",
                kwargs_name="kwargs",
            ),
        ),
        (
            lambda *args_, **kwargs_: None,
            FuncArgsInfo(
                by_name={},
                by_position=[],
                args_name="args_",
                kwargs_name="kwargs_",
            ),
        ),
        (
            lambda x: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=NOT_SET, cached=False)},
                by_position=["x"],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda x=None: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=None, cached=False)},
                by_position=["x"],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda *, x: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=NOT_SET, cached=False)},
                by_position=[],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda *, x=None: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=None, cached=False)},
                by_position=[],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda x, /: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=NOT_SET, cached=False)},
                by_position=["x"],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda x=None, /: None,
            FuncArgsInfo(
                by_name={"x": ArgInfo(position=0, name="x", default=None, cached=False)},
                by_position=["x"],
                args_name=None,
                kwargs_name=None,
            ),
        ),
        (
            lambda a, b, /, c, d=1, *args, e, f=2, **kwargs: None,
            FuncArgsInfo(
                by_name={
                    "a": ArgInfo(position=0, name="a", default=NOT_SET, cached=False),
                    "b": ArgInfo(position=1, name="b", default=NOT_SET, cached=False),
                    "c": ArgInfo(position=2, name="c", default=NOT_SET, cached=False),
                    "d": ArgInfo(position=3, name="d", default=1, cached=False),
                    "e": ArgInfo(position=4, name="e", default=NOT_SET, cached=False),
                    "f": ArgInfo(position=5, name="f", default=2, cached=False),
                },
                by_position=["a", "b", "c", "d"],
                args_name="args",
                kwargs_name="kwargs",
            ),
        ),
    ],
)
def test__collect_args_info(func: Callable, args_info: FuncArgsInfo) -> None:
    assert collect_args_info(func) == args_info


@pytest.mark.parametrize(
    ("func", "args", "kwargs", "result"),
    [
        (func, args, kwargs, call_args)
        for func, possible_calls in TestFunctions.items()
        for (args, kwargs, call_args) in possible_calls
    ],
)
def test__get_call_args(
    func: Callable[..., Any],
    args: list[Any],
    kwargs: dict[str, Any],
    result: dict[str, Any],
):
    by_name, by_position, *_ = collect_args_info(func)
    assert get_call_args(by_name, by_position, args, kwargs) == result
