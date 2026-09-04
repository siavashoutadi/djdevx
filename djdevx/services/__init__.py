"""Pixi-native local dev services (postgres, redis, otel) and resolution."""

from .base import BaseDevService
from .otel import OpenObserveService, OtelCollectorService
from .postgres import PostgresService
from .redis import RedisService
from .registry import (
    register_service,
    resolve_cache_dev_service,
    resolve_database_dev_service,
    resolve_dev_services,
    resolve_openobserve_dev_service,
    resolve_otel_dev_services,
)

__all__ = [
    "BaseDevService",
    "OpenObserveService",
    "OtelCollectorService",
    "PostgresService",
    "RedisService",
    "register_service",
    "resolve_cache_dev_service",
    "resolve_database_dev_service",
    "resolve_dev_services",
    "resolve_openobserve_dev_service",
    "resolve_otel_dev_services",
]
