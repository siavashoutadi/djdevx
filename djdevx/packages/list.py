"""Package list command — shows all available packages in a table."""

from ._base import BasePackage
from ..utils.installable.list_table import build_list_table


def list_packages_table() -> None:
    """List all available packages with install status in a table."""
    build_list_table(BasePackage, "Package")
