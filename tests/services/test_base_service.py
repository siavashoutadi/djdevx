"""Tests for BaseDevService shared helpers (wait_until_ready, step_group, .env.ddx)."""

import os
from unittest.mock import MagicMock, patch

from djdevx.services.base import BaseDevService, _StepGroupWrapper


class _ConcreteService(BaseDevService):
    name = "concrete"
    display_name = "Concrete"
    service_subdir = "concrete"
    data_subdir = "data"

    def up(self, step=None):
        pass

    def down(self, step=None):
        pass

    def is_up(self, step=None):
        return True

    def reset(self, step=None):
        pass


def _make_service(tmp_path, **kwargs):
    return _ConcreteService(project_root=tmp_path, **kwargs)


def test_wait_until_ready_returns_true_when_probe_becomes_true(tmp_path):
    service = _make_service(tmp_path)
    probe = iter([False, False, True])

    def _probe():
        return next(probe)

    with patch("djdevx.services.base.time.sleep"):
        assert service.wait_until_ready(_probe, retries=5) is True


def test_wait_until_ready_returns_false_when_probe_never_true(tmp_path):
    service = _make_service(tmp_path)
    with patch("djdevx.services.base.time.sleep"):
        assert service.wait_until_ready(lambda: False, retries=3) is False


def test_wait_until_ready_ignores_oserror_from_probe(tmp_path):
    service = _make_service(tmp_path)

    def _probe():
        raise OSError("conn refused")

    with patch("djdevx.services.base.time.sleep"):
        assert service.wait_until_ready(_probe, retries=3) is False


def test_step_group_returns_wrapped_parent_step(tmp_path):
    service = _make_service(tmp_path)
    parent = MagicMock()
    # When a parent step is passed, it is returned as-is (no done wrapper).
    assert service.step_group("t", "d", step=parent) is parent


def test_step_group_wraps_standalone_group(tmp_path):
    service = _make_service(tmp_path)
    with patch("djdevx.services.base.print_console.step_group") as mk:
        group = mk.return_value
        wrapped = service.step_group("title", "done")
    assert isinstance(wrapped, _StepGroupWrapper)
    assert wrapped._group is group
    wrapped.ok("child")
    group.ok.assert_called_once_with("child")
    wrapped.done()
    group.done.assert_called_once_with()


class _PortService(BaseDevService):
    """Concrete service that publishes a port (exercises the .env.ddx flow)."""

    name = "portsvc"
    display_name = "PortSvc"
    service_subdir = "portsvc"
    data_subdir = "data"
    port_env_key = "PORTSVC_PORT"

    def up(self, step=None):
        pass

    def down(self, step=None):
        pass

    def is_up(self, step=None):
        return False

    def reset(self, step=None):
        pass


def _read_env_ddx(tmp_path):
    return (tmp_path / ".env.ddx").read_text()


def test_set_port_env_publishes_to_env_ddx(tmp_path):
    service = _PortService(project_root=tmp_path)
    with patch.dict("os.environ", {}, clear=True):
        service._set_port_env(quiet=True)
        assert os.environ["PORTSVC_PORT"] == str(service.port)
    content = _read_env_ddx(tmp_path)
    assert f"PORTSVC_PORT={service.port}" in content
    assert content.startswith("#")


def test_env_ddx_upsert_preserves_other_services(tmp_path):
    first = _PortService(project_root=tmp_path)
    with patch.dict("os.environ", {}, clear=True):
        first._set_port_env(quiet=True)
    (tmp_path / ".env.ddx").write_text("# header\nOTHER_PORT=1234\nPORTSVC_PORT=9999\n")
    with patch.dict("os.environ", {}, clear=True):
        first._set_port_env(quiet=True)
    content = _read_env_ddx(tmp_path)
    assert "OTHER_PORT=1234" in content
    assert f"PORTSVC_PORT={first.port}" in content
    assert "PORTSVC_PORT=9999" not in content


def test_purge_removes_service_line_from_env_ddx(tmp_path):
    service = _PortService(project_root=tmp_path)
    service.data_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".env.ddx").write_text(
        f"# header\nPORTSVC_PORT={service.port}\nOTHER_PORT=1234\n"
    )
    with patch("djdevx.services.base.print_console.step_group"):
        service.purge()
    content = _read_env_ddx(tmp_path)
    assert "OTHER_PORT=1234" in content
    assert "PORTSVC_PORT=" not in content


def test_purge_deletes_env_ddx_when_no_ports_left(tmp_path):
    service = _PortService(project_root=tmp_path)
    service.data_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".env.ddx").write_text(f"# header\nPORTSVC_PORT={service.port}\n")
    with patch("djdevx.services.base.print_console.step_group"):
        service.purge()
    assert not (tmp_path / ".env.ddx").exists()
