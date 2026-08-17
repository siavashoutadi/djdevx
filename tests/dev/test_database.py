"""Tests for ddx dev database {init,reset,purge}."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.utils.django.manage_commands import ManageCommands

runner = CliRunner()


def _data_dir(tmp_path):
    return tmp_path / ".pixi" / "devdata" / "postgres"


def _make_service(tmp_path, is_up=True):
    service = MagicMock()
    service.is_up.return_value = is_up
    service.display_name = "PostgreSQL"
    service.data_dir = _data_dir(tmp_path)
    return service


def _invoke(tmp_path, monkeypatch, args, service, pending=True):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    with (
        patch(
            "djdevx.dev.database.resolve_database_dev_service", return_value=service
        ) as resolve,
        patch("djdevx.dev.database.PixiRunner") as pixi_cls,
        patch.object(
            ManageCommands, "migrations_pending", return_value=pending
        ) as pend,
    ):
        pixi = pixi_cls.return_value
        result = runner.invoke(app, ["dev", "database", *args])
    return result, resolve, pixi, pend


def test_init_starts_and_migrates_when_pending(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=False)
    result, _, pixi, _ = _invoke(tmp_path, monkeypatch, ["init"], service)
    assert result.exit_code == 0
    service.up.assert_called_once()
    pixi.run_manage_command.assert_called_once_with("migrate", check=True)


def test_init_skips_migrate_when_up_to_date(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=True)
    result, _, pixi, _ = _invoke(
        tmp_path, monkeypatch, ["init"], service, pending=False
    )
    assert result.exit_code == 0
    service.up.assert_not_called()
    pixi.run_manage_command.assert_not_called()


def test_reset_flushes_data(tmp_path, monkeypatch):
    service = _make_service(tmp_path)
    result, _, _, _ = _invoke(tmp_path, monkeypatch, ["reset"], service)
    assert result.exit_code == 0
    service.reset.assert_called_once()


def test_purge_stops_and_deletes_data(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=True)
    result, _, _, _ = _invoke(tmp_path, monkeypatch, ["purge"], service)
    assert result.exit_code == 0
    service.down.assert_called_once()
    assert not service.data_dir.exists()


def test_commands_guard_when_no_database(tmp_path, monkeypatch):
    result, _, _, _ = _invoke(tmp_path, monkeypatch, ["init"], None)
    assert result.exit_code == 1
    assert "No database installed" in result.output
