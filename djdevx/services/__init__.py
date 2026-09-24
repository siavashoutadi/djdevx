"""Pixi-native local dev services (postgres, redis, celery, otel) and resolution."""

from .base import BaseDevService
from .celery import CeleryBeatService, CeleryWorkerService
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
    resolve_scheduler_dev_service,
    resolve_task_queue_dev_service,
)

__all__ = [
    "BaseDevService",
    "CeleryBeatService",
    "CeleryWorkerService",
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
    "resolve_scheduler_dev_service",
    "resolve_task_queue_dev_service",
]
