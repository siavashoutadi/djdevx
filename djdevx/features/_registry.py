"""Feature registry — FEATURE_REGISTRY dict and register decorator."""

from ..utils.installable.registry import Registry
from ..utils.installable.types import FEATURE
from ._base import BaseFeature

FEATURE_REGISTRY: Registry[BaseFeature] = Registry(FEATURE)
register = FEATURE_REGISTRY.register
get_feature = FEATURE_REGISTRY.get
list_features = FEATURE_REGISTRY.list
