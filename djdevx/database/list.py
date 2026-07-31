"""Database list command — shows all available databases in a table."""

from ._base import BaseDatabase
from ..utils.installable.list_table import build_list_table


def list_databases_table() -> None:
    """List all available databases with install status in a table."""
    build_list_table(BaseDatabase, "Database")
