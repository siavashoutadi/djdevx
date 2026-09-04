"""Tests for resolve_database_dev_service / resolve_cache_dev_service."""

from djdevx.services import (
    PostgresService,
    RedisService,
    resolve_cache_dev_service,
    resolve_database_dev_service,
    resolve_dev_services,
)
from djdevx.utils.tracking import ProjectTracking, Section


def _track_db(tmp_path, name="postgres"):
    ProjectTracking(tmp_path).add(Section.DATABASE, name, name)


def _track_cache(tmp_path, name="redis"):
    ProjectTracking(tmp_path).add(Section.CACHE, name, name)


def test_database_none_when_not_installed(tmp_path):
    assert resolve_database_dev_service(project_root=tmp_path) is None


def test_cache_none_when_not_installed(tmp_path):
    assert resolve_cache_dev_service(project_root=tmp_path) is None


def test_database_none_when_provider_not_in_map(tmp_path):
    _track_db(tmp_path, "mysql")
    assert resolve_database_dev_service(project_root=tmp_path) is None


def test_cache_none_when_provider_not_in_map(tmp_path):
    _track_cache(tmp_path, "memcached")
    assert resolve_cache_dev_service(project_root=tmp_path) is None


def test_database_returns_postgres_service(tmp_path):
    _track_db(tmp_path)
    service = resolve_database_dev_service(project_root=tmp_path)
    assert isinstance(service, PostgresService)
    assert service.runner.project_root == tmp_path


def test_cache_returns_redis_service(tmp_path):
    _track_cache(tmp_path)
    service = resolve_cache_dev_service(project_root=tmp_path)
    assert isinstance(service, RedisService)
    assert service.runner.project_root == tmp_path


def test_database_passes_verbose(tmp_path):
    _track_db(tmp_path)
    service = resolve_database_dev_service(project_root=tmp_path, verbose=True)
    assert service.verbose is True


def test_cache_passes_verbose(tmp_path):
    _track_cache(tmp_path)
    service = resolve_cache_dev_service(project_root=tmp_path, verbose=True)
    assert service.verbose is True


def test_dev_services_empty_when_nothing_installed(tmp_path):
    assert resolve_dev_services(project_root=tmp_path) == []


def test_dev_services_returns_db_only(tmp_path):
    _track_db(tmp_path)
    services = resolve_dev_services(project_root=tmp_path)
    assert [type(s) for s in services] == [PostgresService]


def test_dev_services_returns_cache_only(tmp_path):
    _track_cache(tmp_path)
    services = resolve_dev_services(project_root=tmp_path)
    assert [type(s) for s in services] == [RedisService]


def test_dev_services_returns_both(tmp_path):
    _track_db(tmp_path)
    _track_cache(tmp_path)
    services = resolve_dev_services(project_root=tmp_path)
    assert [type(s) for s in services] == [PostgresService, RedisService]


def test_dev_services_passes_verbose(tmp_path):
    _track_db(tmp_path)
    services = resolve_dev_services(project_root=tmp_path, verbose=True)
    assert all(s.verbose is True for s in services)
