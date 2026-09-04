"""Tests for RedisService — pixi-native local Redis dev service."""

from unittest.mock import MagicMock, patch

from djdevx.utils.services.redis import RedisService


def make_service(root, returncode=0, stdout="PONG"):
    """Build a RedisService backed by a mocked PixiRunner."""
    with patch("djdevx.utils.services.base.PixiRunner") as mock_cls:
        runner = mock_cls.return_value
        runner.run_pixi_command.return_value = MagicMock(
            returncode=returncode, stdout=stdout
        )
        service = RedisService(project_root=root)
    return service, runner


def _ping_args(port, password):
    return ("run", "redis-cli", "-p", str(port), "-a", password, "ping")


def test_data_dir_under_devdata(tmp_path):
    service, _ = make_service(tmp_path)
    assert service.data_dir == tmp_path / ".pixi" / "devdata" / "redis" / "data"


def test_password_defaults_to_dev_default(tmp_path):
    service, _ = make_service(tmp_path)
    assert service.password == "redis_password"


def test_password_reads_secret_file(tmp_path):
    (tmp_path / ".secrets").mkdir()
    (tmp_path / ".secrets" / "redis_password").write_text("secret-pw")
    service, _ = make_service(tmp_path)
    assert service.password == "secret-pw"


def test_is_up_true_on_pong(tmp_path):
    service, _ = make_service(tmp_path, returncode=0, stdout="PONG")
    assert service.is_up() is True


def test_is_up_false_on_error(tmp_path):
    service, _ = make_service(tmp_path, returncode=1, stdout="")
    assert service.is_up() is False


def test_is_up_false_without_pong(tmp_path):
    service, _ = make_service(tmp_path, returncode=0, stdout="NOAUTH")
    assert service.is_up() is False


def test_up_starts_redis_server(tmp_path):
    not_running = MagicMock(returncode=1, stdout="")
    ok = MagicMock(returncode=0, stdout="")
    pong = MagicMock(returncode=0, stdout="PONG")
    with patch("djdevx.utils.services.base.PixiRunner") as mock_cls:
        runner = mock_cls.return_value
        runner.run_pixi_command.side_effect = [not_running, ok, pong]
        service = RedisService(project_root=tmp_path)
    service.up()
    args = runner.run_pixi_command.call_args_list[1].args
    assert args[:2] == ("run", "redis-server")
    assert args[2:] == (
        "--port",
        str(service.port),
        "--requirepass",
        "redis_password",
        "--dir",
        str(service.data_dir),
        "--daemonize",
        "yes",
        "--appendonly",
        "yes",
    )
    assert service.data_dir.exists()


def test_up_skips_when_running(tmp_path):
    service, runner = make_service(tmp_path)
    service.up()
    assert runner.run_pixi_command.call_count == 1
    assert runner.run_pixi_command.call_args[0] == _ping_args(
        service.port, service.password
    )


def test_down_shuts_down(tmp_path):
    service, runner = make_service(tmp_path)
    service.down()
    args = runner.run_pixi_command.call_args[0]
    assert args == (
        "run",
        "redis-cli",
        "-p",
        str(service.port),
        "-a",
        "redis_password",
        "shutdown",
    )


def test_down_skips_when_not_running(tmp_path):
    service, runner = make_service(tmp_path, returncode=1, stdout="")
    service.down()
    assert runner.run_pixi_command.call_count == 1
    assert runner.run_pixi_command.call_args[0] == _ping_args(
        service.port, service.password
    )


def test_reset_flushall(tmp_path):
    service, runner = make_service(tmp_path)
    service.reset()
    args = runner.run_pixi_command.call_args[0]
    assert args == (
        "run",
        "redis-cli",
        "-p",
        str(service.port),
        "-a",
        "redis_password",
        "FLUSHALL",
    )
