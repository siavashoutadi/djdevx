"""Resolve InstallableRef to its class via the appropriate registry."""

from djdevx.cache._registry import get_cache
from djdevx.database._registry import get_database
from djdevx.features._registry import get_feature
from djdevx.frameworks._registry import get_framework
from djdevx.packages._registry import get_package

from .types import CACHE, DATABASE, FEATURE, FRAMEWORK, PACKAGE, InstallableRef


def resolve(ref: InstallableRef) -> type:
    if ref.kind == PACKAGE:
        return get_package(ref.name)
    if ref.kind == FEATURE:
        return get_feature(ref.name)
    if ref.kind == FRAMEWORK:
        return get_framework(ref.name)
    if ref.kind == DATABASE:
        return get_database(ref.name)
    if ref.kind == CACHE:
        return get_cache(ref.name)
    raise ValueError(f"Unknown installable kind: {ref.kind}")
