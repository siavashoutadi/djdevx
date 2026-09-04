"""Tests for the installable orchestrator's interactive flow."""

from pathlib import Path

from djdevx.core.console import print_console
from djdevx.installable import orchestrator as orch
from djdevx.providers.features.pwa import PWAFeature


def test_add_simple_collects_params_inside_step_group(
    tmp_path: Path, monkeypatch
) -> None:
    """The 'Installing X...' header must be printed before any prompts."""
    (tmp_path / "djdevx.toml").write_text('project_name = "test"\n')
    monkeypatch.chdir(tmp_path)

    order: list[str] = []

    real_step = print_console.step

    def _step(line: str) -> None:
        order.append(f"step:{line}")
        real_step(line)

    monkeypatch.setattr(print_console, "step", _step)
    monkeypatch.setattr(
        orch, "_collect_install_kwargs", lambda _x: order.append("collect") or {}
    )
    monkeypatch.setattr(PWAFeature, "add", lambda self, **kwargs: order.append("add"))

    feature = PWAFeature()
    assert orch._add_simple(feature, "pwa", is_multi=False) is True

    assert order == ["step:Installing PWA...", "collect", "add"]
