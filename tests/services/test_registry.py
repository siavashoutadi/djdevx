"""Tests for the pluggable dev-service registry."""

import pytest

from djdevx.services import (
    OpenObserveService,
    OtelCollectorService,
    PostgresService,
    RedisService,
    register_service,
    resolve_cache_dev_service,
    resolve_database_dev_service,
    resolve_dev_services,
    resolve_openobserve_dev_service,
    resolve_otel_dev_services,
)
from djdevx.services.registry import SERVICE_REGISTRY
from djdevx.utils.tracking import ProjectTracking, Section


def _track(tmp_path, section, name):
    ProjectTracking(tmp_path).add(section, name, name)


def test_builtin_services_registered_with_categories():
    assert SERVICE_REGISTRY["postgres"] is PostgresService
    assert SERVICE_REGISTRY["redis"] is RedisService
    assert SERVICE_REGISTRY["otel"] is OtelCollectorService
    assert SERVICE_REGISTRY["openobserve"] is OpenObserveService
    assert PostgresService.category == "database"
    assert RedisService.category == "cache"
    assert OtelCollectorService.category == "otel"
    assert OpenObserveService.category == "otel"


def test_register_service_rejects_duplicates():
    with pytest.raises(ValueError, match="Duplicate dev service registration"):
        register_service(PostgresService)


def test_register_service_custom_class_roundtrip():
    class _Custom(PostgresService):
        name = "custom-pg"

    try:
        register_service(_Custom)
        assert SERVICE_REGISTRY["custom-pg"] is _Custom
    finally:
        SERVICE_REGISTRY.pop("custom-pg", None)


def test_category_mismatch_is_not_resolved(tmp_path):
    # postgres tracked under CACHE must not resolve as a cache service.
    _track(tmp_path, Section.CACHE, "postgres")
    assert resolve_cache_dev_service(project_root=tmp_path) is None


def test_database_resolves_tracked_postgres(tmp_path):
    _track(tmp_path, Section.DATABASE, "postgres")
    service = resolve_database_dev_service(project_root=tmp_path)
    assert isinstance(service, PostgresService)


def test_otel_none_when_feature_not_installed(tmp_path):
    assert resolve_otel_dev_services(project_root=tmp_path) == []
    assert resolve_openobserve_dev_service(project_root=tmp_path) is None


def test_otel_resolves_both_services_when_feature_installed(tmp_path):
    _track(tmp_path, Section.FEATURES, "otel")
    services = resolve_otel_dev_services(project_root=tmp_path)
    assert [type(s) for s in services] == [OtelCollectorService, OpenObserveService]
    assert isinstance(
        resolve_openobserve_dev_service(project_root=tmp_path), OpenObserveService
    )


def test_resolve_dev_services_ordering(tmp_path):
    _track(tmp_path, Section.DATABASE, "postgres")
    _track(tmp_path, Section.CACHE, "redis")
    _track(tmp_path, Section.FEATURES, "otel")
    names = [s.name for s in resolve_dev_services(project_root=tmp_path)]
    assert names == ["postgres", "redis", "otel", "openobserve"]


def test_resolve_dev_services_skips_missing(tmp_path):
    _track(tmp_path, Section.CACHE, "redis")
    names = [s.name for s in resolve_dev_services(project_root=tmp_path)]
    assert names == ["redis"]
