"""Cache registry — CACHE_REGISTRY dict and register decorator."""

from ..utils.installable.registry import Registry
from ..utils.installable.types import CACHE
from ._base import BaseCache

CACHE_REGISTRY: Registry[BaseCache] = Registry(CACHE)
register = CACHE_REGISTRY.register
get_cache = CACHE_REGISTRY.get
list_caches = CACHE_REGISTRY.list
