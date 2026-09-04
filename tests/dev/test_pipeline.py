"""Tests for the declarative dev start pipeline and dev otel commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from djdevx.cli.dev import run_start
from djdevx.main import app
from djdevx.core.console import print_console
from djdevx.utils.django.manage_commands import ManageCommands

cli = CliRunner()


def _service(calls, tag, is_up=False):
    service = MagicMock()
    service.display_name = "PostgreSQL" if tag == "db" else "Redis"
    service.is_up.return_value = is_up
    service.up.side_effect = lambda step=None: calls.append(f"{tag}_up")
    return service


def _run(
    calls,
    *,
    args=(),
    devcontainer=False,
    skip_settings=False,
    skip_migrate=False,
    db_is_up=False,
    cache_is_up=False,
    no_db=False,
    no_cache=False,
    pending=True,
):
    """Invoke run_start with all external effects mocked, recording order."""
    ctx = MagicMock()
    ctx.args = list(args)
    db = None if no_db else _service(calls, "db", db_is_up)
    cache = None if no_cache else _service(calls, "cache", cache_is_up)
    with (
        patch(
            "djdevx.cli.dev._init_settings",
            side_effect=lambda: calls.append("settings"),
        ),
        patch("djdevx.cli.dev.PixiRunner") as pixi_cls,
        patch("djdevx.cli.dev.resolve_database_dev_service", return_value=db),
        patch("djdevx.cli.dev.resolve_cache_dev_service", return_value=cache),
        patch("djdevx.cli.dev.in_devcontainer", return_value=devcontainer),
        patch.object(
            ManageCommands, "migrations_pending", return_value=pending
        ) as pend,
        patch.object(
            ManageCommands, "run", side_effect=lambda *a, **k: calls.append("migrate")
        ),
        patch(
            "djdevx.cli.dev.render_services_table",
            side_effect=lambda *a: calls.append("render"),
        ),
        patch("djdevx.cli.dev.collect_context", return_value=MagicMock()),
        patch("djdevx.cli.dev.server_command", return_value=("cmd",)),
    ):
        pixi_cls.return_value.run_interactive.side_effect = lambda *a: calls.append(
            "server"
        )
        run_start(
            ctx, skip_settings=skip_settings, skip_migrate=skip_migrate, verbose=False
        )
    return {"db": db, "cache": cache, "pending": pend}


def test_step_order_native():
    calls: list[str] = []
    _run(calls)
    assert calls == ["settings", "db_up", "migrate", "cache_up", "render", "server"]


def test_each_service_started_exactly_once():
    calls: list[str] = []
    result = _run(calls)
    assert result["db"].up.call_count == 1
    assert result["cache"].up.call_count == 1


def test_running_services_are_not_restarted():
    calls: list[str] = []
    result = _run(calls, db_is_up=True, cache_is_up=True)
    assert calls == ["settings", "migrate", "render", "server"]
    result["db"].up.assert_not_called()
    result["cache"].up.assert_not_called()


def test_no_services_configured():
    calls: list[str] = []
    _run(calls, no_db=True, no_cache=True)
    assert calls == ["settings", "migrate", "render", "server"]


def test_no_migrate_when_up_to_date():
    calls: list[str] = []
    _run(calls, pending=False)
    assert "migrate" not in calls
    assert calls == ["settings", "db_up", "cache_up", "render", "server"]


def test_skip_settings_and_migrate():
    calls: list[str] = []
    result = _run(calls, skip_settings=True, skip_migrate=True)
    assert "settings" not in calls
    assert "migrate" not in calls
    result["pending"].assert_not_called()
    assert calls == ["db_up", "cache_up", "render", "server"]


def test_devcontainer_only_migrates():
    calls: list[str] = []
    _run(calls, devcontainer=True)
    assert calls == ["settings", "migrate", "render", "server"]


def test_server_receives_forwarded_args():
    calls: list[str] = []
    _run(calls, args=("--noreload", "8000"))
    assert calls[-1] == "server"


# ---------------------------------------------------------------------------
# ddx dev otel
# ---------------------------------------------------------------------------


def _otel_services(is_up=False):
    services = []
    for display in ("OTel Collector", "OpenObserve"):
        service = MagicMock()
        service.display_name = display
        service.is_up.return_value = is_up
        services.append(service)
    return services


def test_otel_purge_emits_done_exactly_once(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    services = _otel_services()
    with (
        patch("djdevx.dev.otel.resolve_otel_dev_services", return_value=services),
        patch.object(print_console, "step_done") as step_done,
    ):
        result = cli.invoke(app, ["dev", "otel", "purge"])
    assert result.exit_code == 0
    assert step_done.call_count == 1
    for service in services:
        service.purge.assert_called_once()


def test_otel_purge_guard_when_not_installed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    with patch("djdevx.dev.otel.resolve_otel_dev_services", return_value=[]):
        result = cli.invoke(app, ["dev", "otel", "purge"])
    assert result.exit_code == 1
    assert "not installed" in result.output


def test_otel_init_starts_each_service_once(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    services = _otel_services()
    with (
        patch("djdevx.dev.otel.resolve_otel_dev_services", return_value=services),
        patch("djdevx.dev.otel.in_devcontainer", return_value=False),
    ):
        result = cli.invoke(app, ["dev", "otel", "init"])
    assert result.exit_code == 0
    for service in services:
        service.up.assert_called_once()
