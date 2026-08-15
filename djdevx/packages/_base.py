"""BasePackage — thin wrapper over Installable for the packages domain."""

from ..utils.installable.installable import Installable
from ..utils.tracking import Section


class BasePackage(Installable):
    """Base class for Django packages."""

    section: Section = Section.PACKAGES

    @classmethod
    def get_registry(cls):
        from ._registry import PACKAGE_REGISTRY

        return PACKAGE_REGISTRY
