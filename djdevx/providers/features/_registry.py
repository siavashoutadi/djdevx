"""Feature registry — FEATURE_REGISTRY dict and register decorator."""

from ...installable.registry import Registry
from ...installable.models import FEATURE
from ._base import BaseFeature

FEATURE_REGISTRY: Registry[BaseFeature] = Registry(FEATURE)
register = FEATURE_REGISTRY.register
get_feature = FEATURE_REGISTRY.get
list_features = FEATURE_REGISTRY.names
