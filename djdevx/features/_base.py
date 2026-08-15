"""BaseFeature — thin wrapper over Installable for the features domain."""

from ..utils.installable.installable import Installable
from ..utils.tracking import Section


class BaseFeature(Installable):
    """Base class for Django features."""

    section: Section = Section.FEATURES

    @classmethod
    def get_registry(cls):
        from ._registry import FEATURE_REGISTRY

        return FEATURE_REGISTRY
