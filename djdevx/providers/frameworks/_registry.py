"""Framework registry — FRAMEWORK_REGISTRY dict and register decorator."""

from ...installable.registry import Registry
from ...installable.models import FRAMEWORK
from ._base import BaseFramework

FRAMEWORK_REGISTRY: Registry[BaseFramework] = Registry(FRAMEWORK)
register = FRAMEWORK_REGISTRY.register
get_framework = FRAMEWORK_REGISTRY.get
list_frameworks = FRAMEWORK_REGISTRY.names
