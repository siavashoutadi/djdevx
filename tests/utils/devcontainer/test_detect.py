"""Tests for devcontainer detection and compose port helpers."""

from pathlib import Path

from djdevx.utils.devcontainer.detect import (
    DevelopmentContext,
    exported_http_port,
    in_devcontainer,
    read_devcontainer_services,
)


def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "djdevx.toml").write_text("")
    return tmp_path


def test_in_devcontainer_via_env(tmp_path, monkeypatch):
    root = _make_project(tmp_path)
    monkeypatch.setenv("DEVCONTAINER", "true")
    assert in_devcontainer(root) is True


def test_in_devcontainer_false_with_compose_file(tmp_path, monkeypatch):
    """A .devcontainer/ dir alone does not imply we're inside a container."""
    root = _make_project(tmp_path)
    monkeypatch.delenv("DEVCONTAINER", raising=False)
    dc = root / ".devcontainer" / "docker-compose.yaml"
    dc.parent.mkdir(exist_ok=True)
    dc.write_text("services:\n  devcontainer:\n    image: x\n")
    assert in_devcontainer(root) is False


def test_in_devcontainer_false(tmp_path, monkeypatch):
    root = _make_project(tmp_path)
    monkeypatch.delenv("DEVCONTAINER", raising=False)
    assert in_devcontainer(root) is False


def test_read_devcontainer_services(tmp_path):
    root = _make_project(tmp_path)
    dc = root / ".devcontainer" / "docker-compose.yaml"
    dc.parent.mkdir(exist_ok=True)
    dc.write_text("services:\n  db:\n    image: postgres:16\n")
    services = read_devcontainer_services(root)
    assert "db" in services
    assert services["db"]["image"] == "postgres:16"


def test_read_devcontainer_services_missing(tmp_path):
    root = _make_project(tmp_path)
    assert read_devcontainer_services(root) == {}


def test_exported_http_port_bare(tmp_path):
    assert exported_http_port({"ports": ["5080"]}) == 5080


def test_exported_http_port_host_pair(tmp_path):
    assert exported_http_port({"ports": ["127.0.0.1:5080:5080"]}) == 5080


def test_exported_http_port_missing_with_default(tmp_path):
    assert exported_http_port({"ports": []}, default=4318) == 4318


def test_development_context_by_name():
    ctx = DevelopmentContext(in_devcontainer=False, services=[])
    assert ctx.by_name == {}
