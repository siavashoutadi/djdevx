"""Tests for the pixi-native Celery worker/Beat daemon dev services."""

from unittest.mock import MagicMock, patch

from djdevx.services.celery import CeleryBeatService, CeleryWorkerService


class _FakeStep:
    def ok(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        pass

    def done(self) -> None:
        pass


def _make_service(service_cls, tmp_path, monkeypatch):
    (tmp_path / "djdevx.toml").write_text("")
    monkeypatch.setattr("djdevx.services.celery.is_pid_alive", lambda pid: True)
    return service_cls(project_root=tmp_path)


def test_worker_up_launches_pixi_and_is_up(tmp_path, monkeypatch):
    with patch("subprocess.Popen") as popen:
        proc = MagicMock()
        proc.pid = 12345
        popen.return_value = proc
        service = _make_service(CeleryWorkerService, tmp_path, monkeypatch)

        service.up(step=_FakeStep())

        popen.assert_called_once()
        command = popen.call_args.args[0]
        assert command == [
            "pixi",
            "run",
            "celery",
            "-A",
            "applications.celery",
            "worker",
            "--loglevel=info",
        ]
        assert service.is_up()
        assert (service.service_dir / "pid").read_text() == "12345"


def test_beat_launches_with_beat_subcommand(tmp_path, monkeypatch):
    with patch("subprocess.Popen") as popen:
        popen.return_value.pid = 1
        service = _make_service(CeleryBeatService, tmp_path, monkeypatch)

        service.up(step=_FakeStep())

        command = popen.call_args.args[0]
        assert command == [
            "pixi",
            "run",
            "celery",
            "-A",
            "applications.celery",
            "beat",
            "--loglevel=info",
        ]


def test_worker_down_stops_and_clears_pid(tmp_path, monkeypatch):
    with patch("subprocess.Popen") as popen:
        popen.return_value.pid = 12345
        service = _make_service(CeleryWorkerService, tmp_path, monkeypatch)

        service.up(step=_FakeStep())
        assert service.is_up()

        service.down(step=_FakeStep())

        assert not service.is_up()
        assert not (service.service_dir / "pid").exists()


def test_is_up_false_when_pid_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("djdevx.services.celery.is_pid_alive", lambda pid: True)
    (tmp_path / "djdevx.toml").write_text("")
    service = CeleryWorkerService(project_root=tmp_path)
    assert not service.is_up()


def test_describe_down_without_pid(tmp_path, monkeypatch):
    (tmp_path / "djdevx.toml").write_text("")
    service = CeleryWorkerService(project_root=tmp_path)
    assert "no pid file" in service.describe_down()


def test_password_is_empty_when_secret_file_missing(tmp_path, monkeypatch):
    """Portless daemons must not read ``.secrets`` even when the dir exists.

    Regression: with ``secret_file_name == ""`` the path collapsed to
    ``.secrets`` itself, and once settings-secrets init created that directory
    ``collect_context`` raised IsADirectoryError.
    """
    (tmp_path / "djdevx.toml").write_text("")
    (tmp_path / ".secrets").mkdir()
    service = CeleryWorkerService(project_root=tmp_path)
    assert service.password == ""
    assert service.username == ""


def test_collect_context_renders_portless_services(tmp_path):
    """Native context must tolerate portless services without touching .secrets."""
    (tmp_path / "djdevx.toml").write_text("")
    (tmp_path / ".secrets").mkdir()

    from djdevx.dev import context as context_module

    worker = CeleryWorkerService(project_root=tmp_path)
    beat = CeleryBeatService(project_root=tmp_path)
    with (
        patch.object(
            context_module, "resolve_task_queue_dev_service", return_value=worker
        ),
        patch.object(
            context_module, "resolve_scheduler_dev_service", return_value=beat
        ),
        patch.object(context_module, "resolve_database_dev_service", return_value=None),
        patch.object(context_module, "resolve_cache_dev_service", return_value=None),
        patch.object(context_module, "resolve_otel_dev_services", return_value=[]),
    ):
        endpoints = context_module._native_endpoints(tmp_path, verbose=False)

    by_name = {ep.name: ep for ep in endpoints}
    assert "celery" in by_name and "celery-beat" in by_name
    assert by_name["celery"].port == 0
    assert by_name["celery"].host == ""
    assert by_name["celery"].credentials is None
