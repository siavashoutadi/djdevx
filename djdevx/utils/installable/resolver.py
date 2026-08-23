"""Resolve InstallableRef to its class via the appropriate registry."""

from .registry import REGISTRIES
from .types import InstallableConfig, InstallableRef


def resolve(ref: InstallableRef) -> type[InstallableConfig]:
    registry = REGISTRIES.get(ref.kind.name)
    if registry is None:
        raise ValueError(f"Unknown installable kind: {ref.kind}")
    return registry.get(ref.name)
