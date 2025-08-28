import inspect
from typing import Any, Callable

import pytest

from cachium._helpers import NOT_SET, get_arg_default_value


@pytest.mark.parametrize(
    ("func", "arg_num", "expected"),
    [
        (lambda a: None, 0, NOT_SET),
        (lambda a=1: None, 0, 1),
        (lambda a=None: None, 0, None),
        (lambda a, b=2: None, 0, NOT_SET),
        (lambda a=1, b=2: None, 0, 1),
        (lambda a=1, b=2: None, 1, 2),
        (lambda a=1, *, b: None, 1, NOT_SET),
        (lambda a=1, *, b=2: None, 1, NOT_SET),
    ],
    ids=[
        "no default for arg",
        "default for arg",
        "default None",
        "no default for first arg",
        "default for first arg",
        "default for second arg",
        "kwarg",
        "default for arg with kwarg",
    ],
)
def test_get_arg_default_value(func: Callable[..., Any], arg_num: int, expected: Any):
    i = inspect.getfullargspec(func)
    assert get_arg_default_value(i, arg_num) == expected
