"""BaseFeature — thin wrapper over Installable for the features domain."""

from ..utils.installable.installable import Installable


class BaseFeature(Installable):
    """Base class for Django features."""

    section: str = "features"

    @classmethod
    def get_registry(cls):
        from ._registry import FEATURE_REGISTRY

        return FEATURE_REGISTRY
