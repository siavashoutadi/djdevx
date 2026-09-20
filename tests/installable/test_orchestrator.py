"""Tests for the installable orchestrator's interactive flow."""

from pathlib import Path

from djdevx.core.console import print_console
from djdevx.installable import orchestrator as orch
from djdevx.installable.models import Variant
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
        orch,
        "_collect_install_kwargs",
        lambda _x, _answers=None: order.append("collect") or {},
    )
    monkeypatch.setattr(PWAFeature, "add", lambda self, **kwargs: order.append("add"))

    feature = PWAFeature()
    assert orch._add_simple(feature, "pwa", is_multi=False) is True

    assert order == ["step:Installing PWA...", "collect", "add"]


class _FakeAdditive:
    name = "fake"
    display_name = "Fake"

    def __init__(self):
        self.variants = {
            "core": Variant(name="core", display_name="Core", required=True),
            "extra": Variant(name="extra", display_name="Extra"),
        }
        self.exclusive_variants = False

    def reset_state(self):
        pass

    def add(self, **kwargs):
        kwargs.pop("step", None)
        kwargs.pop("variant_name", None)
        kwargs.pop("install_kwargs", None)
        if kwargs:
            raise AssertionError(f"Unexpected kwargs: {kwargs}")


def test_add_additive_variants_installs_requested_variants(monkeypatch) -> None:
    rendered = []

    monkeypatch.setattr(orch, "_auto_install_needs", lambda *_a, **_k: None)
    monkeypatch.setattr(orch, "_collect_install_kwargs", lambda *_a, **_k: {})
    monkeypatch.setattr(orch, "get_installed_variants", lambda *_a, **_k: [])

    def fake_add(self, **kwargs):
        rendered.append(kwargs["variant_name"])

    monkeypatch.setattr(_FakeAdditive, "add", fake_add)

    installable = _FakeAdditive()
    assert (
        orch._add_additive_variants(
            installable,
            "fake",
            provider=None,
            verbose=False,
            is_multi=True,
            variants=["extra"],
        )
        is True
    )

    assert rendered == ["core", "extra"]


def test_add_additive_variants_skips_unknown_requests(monkeypatch) -> None:
    rendered = []

    monkeypatch.setattr(orch, "_auto_install_needs", lambda *_a, **_k: None)
    monkeypatch.setattr(orch, "_collect_install_kwargs", lambda *_a, **_k: {})
    monkeypatch.setattr(orch, "get_installed_variants", lambda *_a, **_k: [])

    def fake_add(self, **kwargs):
        rendered.append(kwargs["variant_name"])

    monkeypatch.setattr(_FakeAdditive, "add", fake_add)

    installable = _FakeAdditive()
    result = orch._add_additive_variants(
        installable,
        "fake",
        provider=None,
        verbose=False,
        is_multi=True,
        variants=["nope"],
    )

    assert result is True
    assert rendered == ["core"]
