"""Tests for BaseDevService shared helpers (wait_until_ready, step_group)."""

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
