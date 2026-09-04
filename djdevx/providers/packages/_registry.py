"""Package registry — PACKAGE_REGISTRY dict and register decorator."""

from ...utils.installable.registry import Registry
from ...utils.installable.types import PACKAGE
from ._base import BasePackage

PACKAGE_REGISTRY: Registry[BasePackage] = Registry(PACKAGE)
register = PACKAGE_REGISTRY.register
get_package = PACKAGE_REGISTRY.get
list_packages = PACKAGE_REGISTRY.names
