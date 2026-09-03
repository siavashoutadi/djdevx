"""Tests for ddx dev up / down / status."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.settings.source import DEV
from djdevx.utils.django.manage_commands import ManageCommands

runner = CliRunner()


def _project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")


def _make_db(is_up=False):
    db = MagicMock()
    db.display_name = "PostgreSQL"
    db.name = "postgres"
    db.is_up.return_value = is_up
    return db


def _make_cache(is_up=False):
    cache = MagicMock()
    cache.display_name = "Redis"
    cache.name = "redis"
    cache.is_up.return_value = is_up
    return cache


# ---------------------------------------------------------------------------
# up
# ---------------------------------------------------------------------------


def test_up_starts_all_down_services(tmp_path, monkeypatch):
    db = _make_db(is_up=False)
    cache = _make_cache(is_up=False)
    _project(tmp_path, monkeypatch)
    with (
        patch(
            "djdevx.utils.services.resolver.resolve_database_dev_service",
            return_value=db,
        ),
        patch(
            "djdevx.utils.services.resolver.resolve_cache_dev_service",
            return_value=cache,
        ),
    ):
        result = runner.invoke(app, ["dev", "up"])
    assert result.exit_code == 0
    db.up.assert_called_once()
    cache.up.assert_called_once()


def test_up_skips_running_services(tmp_path, monkeypatch):
    db = _make_db(is_up=True)
    cache = _make_cache(is_up=True)
    _project(tmp_path, monkeypatch)
    with (
        patch(
            "djdevx.utils.services.resolver.resolve_database_dev_service",
            return_value=db,
        ),
        patch(
            "djdevx.utils.services.resolver.resolve_cache_dev_service",
            return_value=cache,
        ),
    ):
        result = runner.invoke(app, ["dev", "up"])
    assert result.exit_code == 0
    db.up.assert_not_called()
    cache.up.assert_not_called()


# ---------------------------------------------------------------------------
# down
# ---------------------------------------------------------------------------


def test_down_stops_running_services(tmp_path, monkeypatch):
    db = _make_db(is_up=True)
    cache = _make_cache(is_up=True)
    _project(tmp_path, monkeypatch)
    with (
        patch(
            "djdevx.utils.services.resolver.resolve_database_dev_service",
            return_value=db,
        ),
        patch(
            "djdevx.utils.services.resolver.resolve_cache_dev_service",
            return_value=cache,
        ),
    ):
        result = runner.invoke(app, ["dev", "down"])
    assert result.exit_code == 0
    db.down.assert_called_once()
    cache.down.assert_called_once()


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_status_reports_issues_for_down_services(tmp_path, monkeypatch):
    db = _make_db(is_up=False)
    db.describe_down.return_value = "not responding on port 5432"
    cache = _make_cache(is_up=False)
    cache.describe_down.return_value = "not responding on port 6379"
    _project(tmp_path, monkeypatch)
    with (
        patch(
            "djdevx.utils.services.resolver.resolve_database_dev_service",
            return_value=db,
        ),
        patch(
            "djdevx.utils.services.resolver.resolve_cache_dev_service",
            return_value=cache,
        ),
        patch("djdevx.dev.status.PixiRunner") as pixi_cls,
        patch.object(ManageCommands, "migrations_pending", return_value=False),
        patch("djdevx.dev.status.list_secrets"),
        patch("djdevx.dev.status.list_configs"),
    ):
        pixi_cls.return_value = MagicMock()
        result = runner.invoke(app, ["dev", "status"])
    assert result.exit_code == 0
    assert "2 of 2 service(s) are down:" in result.output
    assert "PostgreSQL: not responding on port 5432" in result.output
    assert "Redis: not responding on port 6379" in result.output


def test_status_shows_state_and_settings(tmp_path, monkeypatch):
    db = _make_db(is_up=True)
    cache = _make_cache(is_up=False)
    _project(tmp_path, monkeypatch)
    with (
        patch(
            "djdevx.utils.services.resolver.resolve_database_dev_service",
            return_value=db,
        ),
        patch(
            "djdevx.utils.services.resolver.resolve_cache_dev_service",
            return_value=cache,
        ),
        patch("djdevx.dev.status.PixiRunner") as pixi_cls,
        patch.object(ManageCommands, "migrations_pending", return_value=False),
        patch("djdevx.dev.status.list_secrets") as list_secrets,
        patch("djdevx.dev.status.list_configs") as list_configs,
    ):
        pixi_cls.return_value = MagicMock()
        result = runner.invoke(app, ["dev", "status"])
    assert result.exit_code == 0
    assert "PostgreSQL" in result.output
    assert "Redis" in result.output
    list_secrets.assert_called_once_with(DEV)
    list_configs.assert_called_once_with(DEV)
