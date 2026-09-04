"""Tests for the DockerComposeManager NestedStep output."""

from io import StringIO

from rich.console import Console

from djdevx.core.console import print_console
from djdevx.utils.devcontainer.docker_compose_manager import DockerComposeManager


def _capture():
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    old = print_console._console
    print_console._console = console
    return buf, old


def _restore(old):
    print_console._console = old


def test_add_service_ok_child_is_indented_when_step_given(tmp_path):
    manager = DockerComposeManager(tmp_path)
    buf, old = _capture()
    try:
        with print_console.step_group(
            "Installing Redis", done="Redis installed"
        ) as step:
            manager.add_service(
                {"name": "cache", "image": "redis:7.4-alpine"},
                [{"name": "cache-data", "driver": "local"}],
                step=step,
            )
    finally:
        _restore(old)
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    child = next(line for line in lines if "Added service 'cache'" in line)
    assert child.startswith("  \u2713"), child  # "  ✓ Added service ..."


def test_add_service_top_level_when_no_step(tmp_path):
    manager = DockerComposeManager(tmp_path)
    buf, old = _capture()
    try:
        manager.add_service({"name": "cache", "image": "redis:7.4-alpine"}, [])
    finally:
        _restore(old)
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    child = next(line for line in lines if "Added service 'cache'" in line)
    assert child.startswith("\u2713"), child  # "✓ Added service ..."
    assert not child.startswith("  "), child


def test_remove_service_ok_child_is_indented_when_step_given(tmp_path):
    manager = DockerComposeManager(tmp_path)
    manager.add_service({"name": "cache", "image": "redis:7.4-alpine"}, [])
    buf, old = _capture()
    try:
        with print_console.step_group("Removing Redis", done="Redis removed") as step:
            manager.remove_service(
                {"name": "cache", "image": "redis:7.4-alpine"}, [], step=step
            )
    finally:
        _restore(old)
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    child = next(line for line in lines if "Removed service 'cache'" in line)
    assert child.startswith("  \u2713"), child  # "  ✓ Removed service ..."


def test_remove_service_top_level_when_no_step(tmp_path):
    manager = DockerComposeManager(tmp_path)
    manager.add_service({"name": "cache", "image": "redis:7.4-alpine"}, [])
    buf, old = _capture()
    try:
        manager.remove_service({"name": "cache", "image": "redis:7.4-alpine"}, [])
    finally:
        _restore(old)
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    child = next(line for line in lines if "Removed service 'cache'" in line)
    assert child.startswith("\u2713"), child  # "✓ Removed service ..."
    assert not child.startswith("  "), child
