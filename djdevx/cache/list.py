"""Cache list command — shows all available caches in a table."""

from ._base import BaseCache
from ..utils.installable.list_table import build_list_table


def list_caches_table() -> None:
    """List all available caches with install status in a table."""
    build_list_table(BaseCache, "Cache")
