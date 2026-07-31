"""BaseCache — thin wrapper over InstallableBase for the cache domain."""

from ..utils.installable.installable import Installable


class BaseCache(Installable):
    """Base class for cache backends."""

    section: str = "cache"

    @classmethod
    def get_registry(cls):
        from ._registry import CACHE_REGISTRY

        return CACHE_REGISTRY
