import pytest

from cachium._helpers import build_cache_key_template


@pytest.mark.parametrize(
    "delimiter",
    [
        "\t",
        "\n",
        " ",
        ",",
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        ["a"],
        ["b", "a"],
        ["c", "b", "a"],
    ],
)
def test_build_cache_key_template(delimiter: str, args: list[str]) -> None:
    res = [arg_name + "={" + arg_name + "}" for arg_name in args]
    expected_template = delimiter.join(res)
    assert build_cache_key_template(args, delimiter=delimiter) == expected_template
