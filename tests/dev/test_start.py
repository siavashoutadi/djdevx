"""Tests for ddx dev start — ordering and skip-if-done behavior."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.utils.django.manage_commands import ManageCommands

runner = CliRunner()

SERVER_ARGS = ["run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


class _Invocation:
    """Collects the mocked PixiRunner + patched helpers used by one invocation."""

    def __init__(self):
        self.db = MagicMock()
        self.db.display_name = "PostgreSQL"
        self.db.is_up.return_value = False
        self.cache = MagicMock()
        self.cache.display_name = "Redis"
        self.cache.is_up.return_value = False
        self.pixi = MagicMock()
        self.pixi.project_root = None
        self.log: list[object] = []
        self.db.up = MagicMock(side_effect=lambda *a, **k: self.log.append("db_up"))
        self.cache.up = MagicMock(
            side_effect=lambda *a, **k: self.log.append("cache_up")
        )
        self.pixi.run_interactive = MagicMock(
            side_effect=lambda *a, **k: self.log.append(("server", a))
        )
        self.pixi.run_manage_command = MagicMock(
            side_effect=lambda *a, **k: self.log.append(("manage", a))
        )

    def invoke(self, tmp_path, monkeypatch, args=(), configure=None):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "djdevx.toml").write_text("")
        with (
            patch("djdevx.dev.pipeline.PixiRunner") as self.pixi_cls,
            patch("djdevx.dev.pipeline._init_settings") as self.init_settings,
            patch(
                "djdevx.dev.pipeline.resolve_database_dev_service"
            ) as self.resolve_db,
            patch(
                "djdevx.dev.pipeline.resolve_cache_dev_service"
            ) as self.resolve_cache,
            patch.object(
                ManageCommands, "migrations_pending", return_value=True
            ) as self.migrations_pending,
            patch("djdevx.dev.pipeline.server_command") as self.server_command,
        ):
            self.pixi_cls.return_value = self.pixi
            self.resolve_db.return_value = self.db
            self.resolve_cache.return_value = self.cache
            self.migrations_pending.return_value = True
            self.server_command.return_value = SERVER_ARGS
            if configure is not None:
                configure(self)
            return runner.invoke(app, ["dev", "start", *args])


def test_start_runs_steps_in_order(tmp_path, monkeypatch):
    inv = _Invocation()
    inv.invoke(tmp_path, monkeypatch)
    assert inv.log == [
        "db_up",
        ("manage", ("migrate",)),
        "cache_up",
        ("server", tuple(SERVER_ARGS)),
    ]


def test_start_skips_settings(tmp_path, monkeypatch):
    inv = _Invocation()
    result = inv.invoke(tmp_path, monkeypatch, ["--skip-settings"])
    assert result.exit_code == 0
    inv.init_settings.assert_not_called()


def test_start_skips_migrate(tmp_path, monkeypatch):
    inv = _Invocation()
    inv.invoke(tmp_path, monkeypatch, ["--skip-migrate"])
    inv.migrations_pending.assert_not_called()
    inv.pixi.run_manage_command.assert_not_called()


def test_start_skips_migrate_when_none_pending(tmp_path, monkeypatch):
    inv = _Invocation()
    inv.invoke(
        tmp_path,
        monkeypatch,
        configure=lambda inv: setattr(inv.migrations_pending, "return_value", False),
    )
    inv.pixi.run_manage_command.assert_not_called()
    inv.db.up.assert_called_once()


def test_start_does_not_start_running_db(tmp_path, monkeypatch):
    inv = _Invocation()
    inv.db.is_up.return_value = True
    inv.invoke(tmp_path, monkeypatch)
    inv.db.up.assert_not_called()


def test_start_forwards_extra_args(tmp_path, monkeypatch):
    inv = _Invocation()
    inv.invoke(tmp_path, monkeypatch, ["--port", "9000"])
    inv.pixi.run_interactive.assert_called_once_with(*SERVER_ARGS, "--port", "9000")
