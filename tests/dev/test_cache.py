"""Tests for ddx dev cache {init,reset,purge}."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from djdevx.main import app

runner = CliRunner()


def _make_service(tmp_path, is_up=True):
    service = MagicMock()
    service.is_up.return_value = is_up
    service.display_name = "Redis"
    service.data_dir = tmp_path / ".pixi" / "devdata" / "redis"
    return service


def _invoke(tmp_path, monkeypatch, args, service):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    with patch(
        "djdevx.dev.cache.resolve_cache_dev_service", return_value=service
    ) as resolve:
        result = runner.invoke(app, ["dev", "cache", *args])
    return result, resolve


def test_init_starts_service(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=False)
    result, _ = _invoke(tmp_path, monkeypatch, ["init"], service)
    assert result.exit_code == 0
    service.up.assert_called_once()


def test_init_skips_when_running(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=True)
    result, _ = _invoke(tmp_path, monkeypatch, ["init"], service)
    assert result.exit_code == 0
    service.up.assert_not_called()


def test_reset_flushes_data(tmp_path, monkeypatch):
    service = _make_service(tmp_path)
    result, _ = _invoke(tmp_path, monkeypatch, ["reset"], service)
    assert result.exit_code == 0
    service.reset.assert_called_once()


def test_purge_stops_and_deletes_data(tmp_path, monkeypatch):
    service = _make_service(tmp_path, is_up=True)
    result, _ = _invoke(tmp_path, monkeypatch, ["purge"], service)
    assert result.exit_code == 0
    service.down.assert_called_once()
    assert not service.data_dir.exists()


def test_commands_guard_when_no_cache(tmp_path, monkeypatch):
    result, _ = _invoke(tmp_path, monkeypatch, ["init"], None)
    assert result.exit_code == 1
    assert "No cache installed" in result.output
