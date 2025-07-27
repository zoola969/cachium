import inspect
from typing import Any, Callable

import pytest

from py_cashier import DefaultKeyBuilder, StrKeySerializer
from tests.functions import TestFunctions, func1

_TEST_FILE = inspect.getfile(func1)


@pytest.mark.parametrize(
    ("func", "args", "kwargs", "expected_key"),
    [
        (
            func,
            args,
            kwargs,
            f"{_TEST_FILE}"
            f":{func.__name__}"
            f":{','.join(f'{arg_name}={arg_value}' for arg_name, arg_value in call_args.items())}",
        )
        for func, possible_calls in TestFunctions.items()
        for (args, kwargs, call_args) in possible_calls
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
