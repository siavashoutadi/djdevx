"""Resolve installed providers to their native dev services via tracking."""

from pathlib import Path
from typing import Optional

from ..tracking import ProjectTracking, Section
from .base import BaseDevService
from .postgres import PostgresService
from .redis import RedisService

DATABASE_DEV_SERVICES: dict[str, type[BaseDevService]] = {
    PostgresService.name: PostgresService,
}
CACHE_DEV_SERVICES: dict[str, type[BaseDevService]] = {
    RedisService.name: RedisService,
}


def _resolve_service(
    name: Optional[str],
    services: dict[str, type[BaseDevService]],
    project_root: Optional[Path],
    verbose: bool,
) -> Optional[BaseDevService]:
    service_cls = services.get(name)
    if service_cls is None:
        return None
    return service_cls(project_root=project_root, verbose=verbose)


def resolve_database_dev_service(
    project_root: Optional[Path] = None, verbose: bool = False
) -> Optional[BaseDevService]:
    """Return the dev service for the single installed database, or None."""
    name = ProjectTracking(project_root).installed(Section.DATABASE)
    return _resolve_service(name, DATABASE_DEV_SERVICES, project_root, verbose)


def resolve_cache_dev_service(
    project_root: Optional[Path] = None, verbose: bool = False
) -> Optional[BaseDevService]:
    """Return the dev service for the single installed cache, or None."""
    name = ProjectTracking(project_root).installed(Section.CACHE)
    return _resolve_service(name, CACHE_DEV_SERVICES, project_root, verbose)


def resolve_dev_services(
    project_root: Optional[Path] = None, verbose: bool = False
) -> list[BaseDevService]:
    """Return the installed database and cache dev services (None-filtered)."""
    return [
        s
        for s in (
            resolve_database_dev_service(project_root, verbose),
            resolve_cache_dev_service(project_root, verbose),
        )
        if s is not None
    ]
