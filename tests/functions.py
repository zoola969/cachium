from typing import Any, Callable, NamedTuple


class CallInfo(NamedTuple):
    args: list[Any]
    kwargs: dict[str, Any]
    call_args: dict[str, Any]


TestFunctions: dict[Callable[..., Any], list[CallInfo]] = {}


def func1() -> None:
    return


TestFunctions[func1] = [
    CallInfo(args=[], kwargs={}, call_args={}),
]


def func2(a: int = 0) -> None:
    return


TestFunctions[func2] = [
    CallInfo(args=[1], kwargs={}, call_args={"a": 1}),
    CallInfo(args=[], kwargs={"a": 1}, call_args={"a": 1}),
    CallInfo(args=[], kwargs={}, call_args={"a": 0}),
]


def func3(a: int = 0, *args: Any, b: int = -1) -> None:
    return


TestFunctions[func3] = [
    CallInfo(args=[], kwargs={}, call_args={"a": 0, "b": -1}),
    CallInfo(args=[], kwargs={"a": 1}, call_args={"a": 1, "b": -1}),
    CallInfo(args=[], kwargs={"b": 2}, call_args={"a": 0, "b": 2}),
    CallInfo(args=[1], kwargs={}, call_args={"a": 1, "b": -1}),
    CallInfo(args=[1], kwargs={"b": 2}, call_args={"a": 1, "b": 2}),
    CallInfo(args=[], kwargs={"a": 1, "b": 2}, call_args={"a": 1, "b": 2}),
]


def func4(a: int, /, b: int = 0) -> None:
    return


TestFunctions[func4] = [
    CallInfo(args=[1, 2], kwargs={}, call_args={"a": 1, "b": 2}),
    CallInfo(args=[1], kwargs={}, call_args={"a": 1, "b": 0}),
    CallInfo(args=[1], kwargs={"b": 2}, call_args={"a": 1, "b": 2}),
]


def func5(a: int, /, b: int = 0, *args: Any, c: int, d: int = -1, **kwargs: Any) -> None:
    return


TestFunctions[func5] = [
    CallInfo(args=[1], kwargs={"c": 3}, call_args={"a": 1, "b": 0, "c": 3, "d": -1}),
    CallInfo(args=[1, 2], kwargs={"c": 3}, call_args={"a": 1, "b": 2, "c": 3, "d": -1}),
    CallInfo(args=[1, 2], kwargs={"c": 3, "d": 4}, call_args={"a": 1, "b": 2, "c": 3, "d": 4}),
    CallInfo(args=[1], kwargs={"b": 2, "c": 3}, call_args={"a": 1, "b": 2, "c": 3, "d": -1}),
    CallInfo(args=[1], kwargs={"c": 3, "d": 4}, call_args={"a": 1, "b": 0, "c": 3, "d": 4}),
    CallInfo(args=[1], kwargs={"b": 2, "c": 3, "d": 4}, call_args={"a": 1, "b": 2, "c": 3, "d": 4}),
]

# Check that the functions can be called with the expected arguments
[func(*args, **kwargs) for func, possible_calls in TestFunctions.items() for (args, kwargs, _) in possible_calls]
