"""BaseDatabase — thin wrapper over InstallableBase for the database domain."""

from ..utils.installable.installable import Installable


class BaseDatabase(Installable):
    """Base class for database providers."""

    section: str = "database"

    @classmethod
    def get_registry(cls):
        from ._registry import DATABASE_REGISTRY

        return DATABASE_REGISTRY
