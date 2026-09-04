"""Database CLI — add/remove/list databases with auto-discovery."""

from ...cli.factory import domain_app
from ._base import BaseDatabase
from ._registry import DATABASE_REGISTRY

app = domain_app(
    BaseDatabase,
    label="Database",
    registry=DATABASE_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    single=True,
)
