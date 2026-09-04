"""Service registry — pluggable dev service registration and resolution.

Replaces the hardcoded service dicts that used to live in ``resolver.py`` with
a single :data:`SERVICE_REGISTRY`. Built-in services register themselves here
via :func:`register_service`; external/pluggable services can call the same
function to add themselves. Resolvers look up services by the provider name
tracked in ``djdevx.toml`` and filter by
:attr:`~BaseDevService.category` so database/cache/otel stay first-class groups.

Ordering of :func:`resolve_dev_services` is deterministic and matches the
pre-refactor behaviour: database (postgres), then cache (redis), then otel
(collector, openobserve).
"""

from pathlib import Path

from ..tracking import ProjectTracking, Section
from .base import BaseDevService
from .otel import OpenObserveService, OtelCollectorService
from .postgres import PostgresService
from .redis import RedisService

SERVICE_REGISTRY: dict[str, type[BaseDevService]] = {}


def register_service[S: BaseDevService](cls: type[S]) -> type[S]:
    """Register a dev service class keyed by its ``name``."""
    if cls.name in SERVICE_REGISTRY:
        raise ValueError(f"Duplicate dev service registration: {cls.name}")
    SERVICE_REGISTRY[cls.name] = cls
    return cls


# Built-in dev services (registered at import time so resolution always sees
# them even if a call site never imports a specific service module).
register_service(PostgresService)
register_service(RedisService)
register_service(OtelCollectorService)
register_service(OpenObserveService)


def _services_by_category(category: str) -> list[type[BaseDevService]]:
    # SERVICE_REGISTRY preserves insertion order, so resolution ordering is stable.
    return [cls for cls in SERVICE_REGISTRY.values() if cls.category == category]


def _resolve_service(
    category: str,
    name: str | None,
    project_root: Path | None,
    verbose: bool,
) -> BaseDevService | None:
    cls = SERVICE_REGISTRY.get(name)
    if cls is None or cls.category != category:
        return None
    return cls(project_root=project_root, verbose=verbose)


def resolve_database_dev_service(
    project_root: Path | None = None, verbose: bool = False
) -> BaseDevService | None:
    """Return the dev service for the single installed database, or None."""
    name = ProjectTracking(project_root).installed(Section.DATABASE)
    return _resolve_service("database", name, project_root, verbose)


def resolve_cache_dev_service(
    project_root: Path | None = None, verbose: bool = False
) -> BaseDevService | None:
    """Return the dev service for the single installed cache, or None."""
    name = ProjectTracking(project_root).installed(Section.CACHE)
    return _resolve_service("cache", name, project_root, verbose)


def resolve_otel_dev_services(
    project_root: Path | None = None, verbose: bool = False
) -> list[BaseDevService]:
    """Return the OTel dev services (collector + OpenObserve), if installed."""
    tracking = ProjectTracking(project_root)
    if not tracking.is_installed(Section.FEATURES, "otel"):
        return []
    return [
        cls(project_root=project_root, verbose=verbose)
        for cls in _services_by_category("otel")
    ]


def resolve_openobserve_dev_service(
    project_root: Path | None = None, verbose: bool = False
) -> BaseDevService | None:
    """Return the OpenObserve dev service if the otel feature is installed."""
    tracking = ProjectTracking(project_root)
    if not tracking.is_installed(Section.FEATURES, "otel"):
        return None
    cls = SERVICE_REGISTRY.get("openobserve")
    if cls is None or cls.category != "otel":
        return None
    return cls(project_root=project_root, verbose=verbose)


def resolve_dev_services(
    project_root: Path | None = None, verbose: bool = False
) -> list[BaseDevService]:
    """Return the installed database and cache dev services (None-filtered)."""
    return [
        s
        for s in (
            resolve_database_dev_service(project_root, verbose),
            resolve_cache_dev_service(project_root, verbose),
            *resolve_otel_dev_services(project_root, verbose),
        )
        if s is not None
    ]
