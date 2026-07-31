"""Framework list command — shows all available frameworks in a table."""

from ._base import BaseFramework
from ..utils.installable.list_table import build_list_table


def list_frameworks_table() -> None:
    """List all available frameworks with install status in a table."""
    build_list_table(BaseFramework, "Framework")
