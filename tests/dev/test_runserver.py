"""Tests for ddx dev runserver and server-command selection."""

from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.dev.runserver import server_command
from djdevx.main import app
from djdevx.core.process import PixiRunner

runner = CliRunner()

PLAIN_SERVER = ("run", "python", "manage.py", "runserver", "0.0.0.0:8000")
TAILWIND_SERVER = ("run", "python", "manage.py", "tailwind", "runserver")


# ---------------------------------------------------------------------------
# server_command (unit)
# ---------------------------------------------------------------------------


def test_server_command_plain(tmp_path):
    (tmp_path / "djdevx.toml").write_text("")
    assert server_command(PixiRunner(project_root=tmp_path)) == list(PLAIN_SERVER)


def test_server_command_tailwind(tmp_path):
    (tmp_path / "djdevx.toml").write_text(
        "[packages.django-tailwind-cli]\ninstalled = true\n"
    )
    assert server_command(PixiRunner(project_root=tmp_path)) == list(TAILWIND_SERVER)


# ---------------------------------------------------------------------------
# ddx dev runserver (CLI)
# ---------------------------------------------------------------------------


def _invoke(tmp_path, monkeypatch, args, toml=""):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text(toml)
    with patch("djdevx.dev.runserver.PixiRunner") as mock_cls:
        pixi = mock_cls.return_value
        pixi.project_root = tmp_path
        result = runner.invoke(app, ["dev", "runserver", *args])
    return result, pixi


def test_runserver_runs_plain_command(tmp_path, monkeypatch):
    result, pixi = _invoke(tmp_path, monkeypatch, [])
    assert result.exit_code == 0
    pixi.run_interactive.assert_called_once_with(*PLAIN_SERVER)


def test_runserver_runs_tailwind_command(tmp_path, monkeypatch):
    result, pixi = _invoke(
        tmp_path,
        monkeypatch,
        [],
        toml="[packages.django-tailwind-cli]\ninstalled = true\n",
    )
    assert result.exit_code == 0
    pixi.run_interactive.assert_called_once_with(*TAILWIND_SERVER)


def test_runserver_forwards_extra_args(tmp_path, monkeypatch):
    result, pixi = _invoke(tmp_path, monkeypatch, ["--port", "9000"])
    assert result.exit_code == 0
    pixi.run_interactive.assert_called_once_with(*PLAIN_SERVER, "--port", "9000")


def test_runserver_forwards_help(tmp_path, monkeypatch):
    result, pixi = _invoke(tmp_path, monkeypatch, ["--help"])
    assert result.exit_code == 0
    pixi.run_interactive.assert_called_once_with(*PLAIN_SERVER, "--help")
