import inspect
from typing import Any, Callable

import pytest

from cachium._helpers import NOT_SET, NoKwargsError, get_kwarg_default_value


@pytest.mark.parametrize(
    ("func", "kwarg_name", "expected"),
    [
        (lambda a, *, b: None, "b", NOT_SET),
        (lambda a, *, b=1: None, "b", 1),
        (lambda a, *, b, c: None, "c", NOT_SET),
        (lambda a, *, b, c=2: None, "c", 2),
    ],
    ids=[
        "no default for kwarg",
        "default for kwarg",
        "no default for second kwarg",
        "default for second kwarg",
    ],
)
def test__get_kwarg_default_value(func: Callable[..., Any], kwarg_name: str, expected: Any):
    i = inspect.getfullargspec(func)
    assert get_kwarg_default_value(i, kwarg_name) == expected


@pytest.mark.parametrize(
    ("func", "kwarg_name"),
    [
        (lambda a: None, "a"),
        (lambda a=1: None, "a"),
        (lambda a, *, b: None, "a"),
        (lambda *, b=2: None, "c"),
        (lambda **kwargs: None, "a"),
    ],
)
def test__get_kwarg_default_value__error(func: Callable[..., Any], kwarg_name: str):
    i = inspect.getfullargspec(func)
    with pytest.raises(NoKwargsError):
        get_kwarg_default_value(i, kwarg_name)
