"""Tests for PostgresService — pixi-native local PostgreSQL dev service."""

from unittest.mock import MagicMock, patch

from djdevx.services.postgres import PostgresService


def make_service(root, returncode=0, stdout="", side_effect=None):
    """Build a PostgresService backed by a mocked PixiRunner."""
    with patch("djdevx.services.base.PixiRunner") as mock_cls:
        runner = mock_cls.return_value
        if side_effect is not None:
            runner.run_pixi_command.side_effect = side_effect
        else:
            runner.run_pixi_command.return_value = MagicMock(
                returncode=returncode, stdout=stdout
            )
        service = PostgresService(project_root=root)
    return service, runner


def _pg_isready_args(port):
    return ("run", "pg_isready", "-h", "localhost", "-p", str(port))


def test_data_dir_under_devdata(tmp_path):
    service, _ = make_service(tmp_path)
    assert service.data_dir == tmp_path / ".pixi" / "devdata" / "postgres"


def test_password_defaults_to_dev_default(tmp_path):
    service, _ = make_service(tmp_path)
    assert service.password == "password"


def test_password_reads_secret_file(tmp_path):
    (tmp_path / ".secrets").mkdir()
    (tmp_path / ".secrets" / "postgres_password").write_text("secret-pw")
    service, _ = make_service(tmp_path)
    assert service.password == "secret-pw"


def test_is_up_true_when_pg_isready_ok(tmp_path):
    service, _ = make_service(tmp_path, returncode=0)
    assert service.is_up() is True


def test_is_up_false_when_pg_isready_fails(tmp_path):
    service, _ = make_service(tmp_path, returncode=1)
    assert service.is_up() is False


def test_describe_down_mentions_log_when_initialized(tmp_path):
    service, _ = make_service(tmp_path)
    service.data_dir.mkdir(parents=True)
    (service.data_dir / "PG_VERSION").write_text("16\n")
    (service.service_dir / "postgres.log").write_text("")
    reason = service.describe_down()
    assert "not responding on port" in reason
    assert "postgres.log" in reason


def test_describe_down_plain_when_not_initialized(tmp_path):
    service, _ = make_service(tmp_path)
    assert service.describe_down() == f"not responding on port {service.port}"


def test_initdb_command(tmp_path):
    service, runner = make_service(tmp_path)
    service._init_db()
    args = runner.run_pixi_command.call_args[0]
    assert args == (
        "run",
        "initdb",
        "-D",
        str(service.data_dir),
        "-U",
        "postgres",
        f"--pwfile={service._pwfile}",
        "-A",
        "scram-sha-256",
    )
    assert runner.run_pixi_command.call_args[1]["check"] is False
    assert not service._pwfile.exists()


def test_start_command(tmp_path):
    service, runner = make_service(tmp_path)
    service._start()
    args = runner.run_pixi_command.call_args[0]
    assert args == (
        "run",
        "pg_ctl",
        "-D",
        str(service.data_dir),
        "-l",
        str(service._log_file),
        "-o",
        f"-p {service.port}",
        "start",
    )


def test_stop_command(tmp_path):
    service, runner = make_service(tmp_path)
    service.down()
    args = runner.run_pixi_command.call_args[0]
    assert args == ("run", "pg_ctl", "-D", str(service.data_dir), "stop")


def test_down_skips_when_not_running(tmp_path):
    service, runner = make_service(tmp_path, returncode=1)
    service.down()
    assert runner.run_pixi_command.call_count == 1
    assert runner.run_pixi_command.call_args[0] == _pg_isready_args(service.port)


def test_reset_flushes_django(tmp_path):
    service, runner = make_service(tmp_path)
    service.reset()
    runner.run_manage_command.assert_called_once_with("flush", "--noinput", check=False)


def test_purge_stops_then_removes_service_dir(tmp_path):
    ok = MagicMock(returncode=0, stdout=b"")
    # order: purge is_up (up), down is_up (up), pg_ctl stop
    service, runner = make_service(tmp_path, side_effect=[ok, ok, ok])
    service.data_dir.mkdir(parents=True)
    (service.data_dir / "PG_VERSION").write_text("16\n")
    port = service.port
    service.purge()
    calls = [c.args for c in runner.run_pixi_command.call_args_list]
    assert calls[0] == _pg_isready_args(port)
    assert calls[1] == _pg_isready_args(port)
    assert calls[2] == ("run", "pg_ctl", "-D", str(service.data_dir), "stop")
    assert not service.service_dir.exists()


def test_purge_skips_stop_when_not_running(tmp_path):
    not_ready = MagicMock(returncode=1, stdout=b"")
    service, runner = make_service(tmp_path, side_effect=[not_ready])
    service.purge()
    assert runner.run_pixi_command.call_count == 1
    assert not service.service_dir.exists()


def test_up_initializes_then_starts(tmp_path):
    ok = MagicMock(returncode=0, stdout=b"")
    not_ready = MagicMock(returncode=1, stdout=b"")
    # order: pg_isready (down), initdb, pg_ctl start, pg_isready (ready probe)
    side_effects = [not_ready, ok, ok, ok]
    service, runner = make_service(tmp_path, side_effect=side_effects)
    service.up()
    calls = [c.args for c in runner.run_pixi_command.call_args_list]
    assert calls[0] == _pg_isready_args(service.port)
    assert calls[1][1] == "initdb"
    assert calls[2][1] == "pg_ctl"
    assert calls[2][-1] == "start"
    assert calls[3] == _pg_isready_args(service.port)


def test_up_skips_start_when_already_running(tmp_path):
    service, runner = make_service(tmp_path, returncode=0)
    service.data_dir.mkdir(parents=True)
    (service.data_dir / "PG_VERSION").write_text("16\n")
    service.up()
    assert runner.run_pixi_command.call_count == 1
    assert runner.run_pixi_command.call_args[0] == _pg_isready_args(service.port)


def test_up_sets_port_env(tmp_path):
    ok = MagicMock(returncode=0, stdout=b"")
    not_ready = MagicMock(returncode=1, stdout=b"")
    service, _ = make_service(tmp_path, side_effect=[not_ready, ok, ok, ok])
    service.up()
    import os

    assert os.environ.get("POSTGRES_PORT") == str(service.port)
    del os.environ["POSTGRES_PORT"]


def test_initdb_failure_raises(tmp_path):
    fail = MagicMock(returncode=1, stderr=b"initdb error detail")
    service, _ = make_service(tmp_path, side_effect=[fail])
    import pytest

    with pytest.raises(RuntimeError, match="initdb failed"):
        service._init_db()


def test_start_failure_raises(tmp_path):
    fail = MagicMock(returncode=1)
    service, _ = make_service(tmp_path, side_effect=[fail])
    import pytest

    with pytest.raises(RuntimeError, match="pg_ctl start failed"):
        service._start()


def test_up_raises_when_not_ready(tmp_path):
    """Once started, a DB that never answers pg_isready raises on up()."""
    import pytest

    ok = MagicMock(returncode=0, stdout=b"")
    not_ready = MagicMock(returncode=1, stdout=b"")

    def side_effect(*args, **kwargs):
        return not_ready if "pg_isready" in args else ok

    service, _ = make_service(tmp_path, side_effect=side_effect)
    with (
        patch("djdevx.services.base.time.sleep"),
        pytest.raises(RuntimeError, match="did not become ready"),
    ):
        service.up()


def test_up_emits_step_group_children(tmp_path):
    """Starting a DB renders a single nested step with ✓ children."""
    from io import StringIO

    from rich.console import Console

    from djdevx.core.console import print_console

    ok = MagicMock(returncode=0, stdout=b"")
    not_ready = MagicMock(returncode=1, stdout=b"")
    # order: pg_isready (down), initdb, pg_ctl start, pg_isready (ready probe)
    service, _ = make_service(tmp_path, side_effect=[not_ready, ok, ok, ok])

    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    old = print_console._console
    print_console._console = console
    try:
        service.up()
    finally:
        print_console._console = old
    out = buf.getvalue()
    assert "Starting PostgreSQL" in out
    assert "initialized postgresql data directory" in out
    assert "started postgresql on port" in out
    assert "set POSTGRES_PORT" in out
