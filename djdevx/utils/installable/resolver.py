"""Resolve InstallableRef to its class via the appropriate registry."""

from .registry import REGISTRIES, Registry
from .types import InstallableConfig, InstallableRef


def resolve(
    ref: InstallableRef, registries: list[Registry] | None = None
) -> type[InstallableConfig]:
    registries = registries if registries is not None else list(REGISTRIES.values())
    for registry in registries:
        if registry.kind != ref.kind:
            continue
        try:
            return registry.get(ref.name)
        except KeyError:
            continue
    raise KeyError(f"No registered installable for {ref!r}")
