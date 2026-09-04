"""Tests for dev context endpoint collection (native + devcontainer)."""

from unittest.mock import MagicMock, patch

from djdevx.dev.context import collect_context


def _mock_service(name, display_name, port, password):
    service = MagicMock()
    service.name = name
    service.display_name = display_name
    service.port = port
    service.password = password
    return service


def test_native_endpoints_use_resolved_passwords(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    db = _mock_service("postgres", "PostgreSQL", 55432, "s3cr3t")
    cache = _mock_service("redis", "Redis", 56379, "r3dis")
    with (
        patch("djdevx.dev.context.in_devcontainer", return_value=False),
        patch("djdevx.dev.context.resolve_database_dev_service", return_value=db),
        patch("djdevx.dev.context.resolve_cache_dev_service", return_value=cache),
    ):
        ctx = collect_context(project_root=tmp_path)
    assert ctx.in_devcontainer is False
    by_name = ctx.by_name
    assert by_name["postgres"].port == 55432
    assert by_name["postgres"].credentials == "s3cr3t"
    assert by_name["redis"].port == 56379
    assert by_name["redis"].credentials == "r3dis"


def test_native_credentials_none_without_password(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    db = _mock_service("postgres", "PostgreSQL", 5432, "")
    with (
        patch("djdevx.dev.context.in_devcontainer", return_value=False),
        patch("djdevx.dev.context.resolve_database_dev_service", return_value=db),
        patch("djdevx.dev.context.resolve_cache_dev_service", return_value=None),
    ):
        ctx = collect_context(project_root=tmp_path)
    assert ctx.services[0].credentials is None


def test_devcontainer_endpoints_from_compose(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    compose_services = {
        "db": {"ports": ["5432"]},
        "cache": {"ports": ["127.0.0.1:6379:6379"]},
    }
    with (
        patch("djdevx.dev.context.in_devcontainer", return_value=True),
        patch(
            "djdevx.dev.context.read_devcontainer_services",
            return_value=compose_services,
        ),
    ):
        ctx = collect_context(project_root=tmp_path)
    assert ctx.in_devcontainer is True
    assert ctx.compose_path == tmp_path / ".devcontainer" / "docker-compose.yaml"
    by_name = ctx.by_name
    assert by_name["db"].display_name == "PostgreSQL"
    assert by_name["db"].port == 5432
    assert by_name["cache"].port == 6379


def test_devcontainer_missing_compose_service_skipped(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    with (
        patch("djdevx.dev.context.in_devcontainer", return_value=True),
        patch(
            "djdevx.dev.context.read_devcontainer_services",
            return_value={"db": {"ports": ["5432"]}},
        ),
    ):
        ctx = collect_context(project_root=tmp_path)
    assert [s.name for s in ctx.services] == ["db"]
