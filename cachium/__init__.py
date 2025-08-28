from importlib.metadata import version

from ._decorators import cache
from ._helpers import CacheWith

__version__ = version("cachium")


__all__ = [
    "CacheWith",
    "cache",
]
