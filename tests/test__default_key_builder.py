import inspect
from typing import Any, Callable

import pytest

from py_cashier import DefaultKeyBuilder, StrKeySerializer


def func1() -> None:
    return


def func2(a: int) -> None:
    return


def func3(a: int, b: str) -> None:
    return


def func4(a: int, *, b: str) -> None:
    return


def func5(a: int, b: str, /) -> None:
    return


def func6(a: int = 0) -> None:
    return


def func7(a: int, b: str = "0") -> None:
    return


def func8(*, a: int, b: str = "0") -> None:
    return


def func9(a: int, b: str = "0", *, c: int, d: str = "0") -> None:
    return


@pytest.mark.parametrize(
    ("func", "args", "kwargs", "result"),
    [
        (func1, [], {}, {}),
        (func2, [1], {}, {"a": "1"}),
        (func2, [], {"a": 1}, {"a": "1"}),
        (func3, [1], {"b": "1"}, {"a": "1", "b": "1"}),
        (func3, [1, "1"], {}, {"a": "1", "b": "1"}),
        (func3, [], {"a": 1, "b": "1"}, {"a": "1", "b": "1"}),
        (func4, [1], {"b": "1"}, {"a": "1", "b": "1"}),
        (func4, [], {"a": 1, "b": "1"}, {"a": "1", "b": "1"}),
        (func5, [1, "1"], {}, {"a": "1", "b": "1"}),
        (func6, [], {}, {"a": "0"}),
        (func6, [1], {}, {"a": "1"}),
        (func6, [], {"a": 1}, {"a": "1"}),
        (func7, [1], {}, {"a": "1", "b": "0"}),
        (func7, [1, "1"], {}, {"a": "1", "b": "1"}),
        (func7, [], {"a": 1}, {"a": "1", "b": "0"}),
        (func7, [], {"a": 1, "b": "1"}, {"a": "1", "b": "1"}),
        (func8, [], {"a": 1}, {"a": "1", "b": "0"}),
        (func8, [], {"a": 1, "b": "1"}, {"a": "1", "b": "1"}),
        (func9, [1], {"c": 1}, {"a": "1", "b": "0", "c": "1", "d": "0"}),
        (func9, [1, "1"], {"c": 1}, {"a": "1", "b": "1", "c": "1", "d": "0"}),
        (func9, [1], {"b": "1", "c": 1}, {"a": "1", "b": "1", "c": "1", "d": "0"}),
        (func9, [1], {"b": "1", "c": "1", "d": "1"}, {"a": "1", "b": "1", "c": "1", "d": "1"}),
        (func9, [], {"a": 1, "b": "1", "c": "1"}, {"a": "1", "b": "1", "c": "1", "d": "0"}),
        (func9, [], {"a": 1, "b": "1", "c": "1", "d": "1"}, {"a": "1", "b": "1", "c": "1", "d": "1"}),
    ],
)
def test__default_key_builder__get_call_args(
    func: Callable[..., Any],
    args: list[Any],
    kwargs: dict[str, Any],
    result: dict[str, Any],
):
    assert DefaultKeyBuilder(func=func, key_serializer=StrKeySerializer)._get_call_args(*args, **kwargs) == result


_TEST_FILE = inspect.getfile(lambda: None)


@pytest.mark.parametrize(
    ("func", "args", "kwargs", "expected_key"),
    [
        (func1, [], {}, f"{_TEST_FILE}:func1:"),
        (func2, [1], {}, f"{_TEST_FILE}:func2:a=1"),
        (func2, [], {"a": 1}, f"{_TEST_FILE}:func2:a=1"),
        (func3, [1], {"b": "1"}, f"{_TEST_FILE}:func3:a=1,b=1"),
        (func3, [1, "1"], {}, f"{_TEST_FILE}:func3:a=1,b=1"),
        (func3, [], {"a": 1, "b": "1"}, f"{_TEST_FILE}:func3:a=1,b=1"),
        (func4, [1], {"b": "1"}, f"{_TEST_FILE}:func4:a=1,b=1"),
        (func4, [], {"a": 1, "b": "1"}, f"{_TEST_FILE}:func4:a=1,b=1"),
        (func5, [1, "1"], {}, f"{_TEST_FILE}:func5:a=1,b=1"),
        (func6, [], {}, f"{_TEST_FILE}:func6:a=0"),
        (func6, [1], {}, f"{_TEST_FILE}:func6:a=1"),
        (func6, [], {"a": 1}, f"{_TEST_FILE}:func6:a=1"),
        (func7, [1], {}, f"{_TEST_FILE}:func7:a=1,b=0"),
        (func7, [1, "1"], {}, f"{_TEST_FILE}:func7:a=1,b=1"),
        (func7, [], {"a": 1}, f"{_TEST_FILE}:func7:a=1,b=0"),
        (func7, [], {"a": 1, "b": "1"}, f"{_TEST_FILE}:func7:a=1,b=1"),
        (func8, [], {"a": 1}, f"{_TEST_FILE}:func8:a=1,b=0"),
        (func8, [], {"a": 1, "b": "1"}, f"{_TEST_FILE}:func8:a=1,b=1"),
        (func9, [1], {"c": 1}, f"{_TEST_FILE}:func9:a=1,b=0,c=1,d=0"),
        (func9, [1, "1"], {"c": 1}, f"{_TEST_FILE}:func9:a=1,b=1,c=1,d=0"),
        (func9, [1], {"b": "1", "c": 1}, f"{_TEST_FILE}:func9:a=1,b=1,c=1,d=0"),
        (func9, [1], {"b": "1", "c": 1, "d": "1"}, f"{_TEST_FILE}:func9:a=1,b=1,c=1,d=1"),
        (func9, [], {"a": 1, "b": "1", "c": 1}, f"{_TEST_FILE}:func9:a=1,b=1,c=1,d=0"),
        (func9, [], {"a": 1, "b": "1", "c": 1, "d": "1"}, f"{_TEST_FILE}:func9:a=1,b=1,c=1,d=1"),
    ],
)
def test__default_key_builder__build_key(
    func: Callable[..., Any],
    args: list[Any],
    kwargs: dict[str, Any],
    expected_key: str,
):
    assert (
        DefaultKeyBuilder(func=func, key_serializer=StrKeySerializer, delimiter=",").build_key(*args, **kwargs)
        == expected_key
    )
