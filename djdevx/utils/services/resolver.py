"""Resolve installed providers to their native dev services.

Backward-compatible shim over :mod:`djdevx.utils.services.registry`. The
registry-backed resolution lives there; this module keeps the historical
import path (``djdevx.utils.services.resolver.resolve_*``) working.
"""

from .registry import (
    resolve_cache_dev_service,
    resolve_database_dev_service,
    resolve_dev_services,
    resolve_openobserve_dev_service,
    resolve_otel_dev_services,
)

__all__ = [
    "resolve_cache_dev_service",
    "resolve_database_dev_service",
    "resolve_dev_services",
    "resolve_openobserve_dev_service",
    "resolve_otel_dev_services",
]
