"""BasePackage — thin wrapper over Installable for the packages domain."""

from ..utils.installable.installable import Installable


class BasePackage(Installable):
    """Base class for Django packages."""

    section: str = "packages"

    @classmethod
    def get_registry(cls):
        from ._registry import PACKAGE_REGISTRY

        return PACKAGE_REGISTRY
