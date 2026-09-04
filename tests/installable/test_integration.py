"""Unit tests for the peer integration engine (utils/installable/peers.py)."""

import os

from pathlib import Path
from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from djdevx.main import app
from djdevx.providers.packages._registry import PACKAGE_REGISTRY
from djdevx.providers.packages.whitenoise import WhitenoisePackage
from djdevx.installable.peers import (
    call_peer,
    sync_on_add,
    sync_on_remove,
    copy_peer_templates,
    cleanup_peer_templates,
    cleanup_all_peer_templates,
)
from djdevx.installable.lifecycle import Installable
from djdevx.installable.ops.pixi import PixiOps
from djdevx.installable.registry import Registry
from djdevx.installable.ops.secrets import SecretsOps
from djdevx.installable.models import (
    FRAMEWORK,
    PACKAGE,
    InstallableRef,
    Variant,
)
from djdevx.utils.tracking import ProjectTracking, Section
from djdevx.utils.types.pixi_types import PixiPackageSpec
from tests.test_helpers import create_test_django_project

CALLS: list[tuple] = []


@pytest.fixture(autouse=True)
def _reset_calls():
    CALLS.clear()
    yield
    CALLS.clear()


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Project root with a hand-seeded djdevx.toml."""
    (tmp_path / "djdevx.toml").write_text('project_name = "test"\n')
    return tmp_path


def track(root: Path, section: Section, name: str, variants=None) -> None:
    ProjectTracking(root).add(section, name, name.title(), variants=variants)


# ── Dummy installables ─────────────────────────────────────────────────────────


class FwPeer(Installable):
    name: str = "bootstrap"
    display_name: str = "Bootstrap"
    section: Section = Section.FRAMEWORKS


class OtherFwPeer(Installable):
    name: str = "tailwind-cli"
    display_name: str = "Tailwind CLI"
    section: Section = Section.FRAMEWORKS


class ListenerPackage(Installable):
    """Listens to any framework; records hook calls in CALLS."""

    name: str = "listener"
    display_name: str = "Listener"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="listener-extra", kind="pypi"),
        ]
    }

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, variant.name if variant else None))

    def on_peer_removed(self, peer, variant=None) -> None:
        CALLS.append(("removed", peer.name, variant.name if variant else None))


class NamedListenerPackage(ListenerPackage):
    """Listens only to a specific framework (bootstrap)."""

    name: str = "named-listener"
    display_name: str = "Named Listener"
    peer_pixi_packages: dict = {
        InstallableRef(kind=FRAMEWORK, name="bootstrap"): [
            PixiPackageSpec(name="listener-extra", kind="pypi"),
        ]
    }


class UninterestedPackage(Installable):
    name: str = "uninterested"
    display_name: str = "Uninterested"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {}

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))


class RaisingListenerPackage(Installable):
    name: str = "raising-listener"
    display_name: str = "Raising Listener"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="raising-extra", kind="pypi"),
        ]
    }

    def on_peer_added(self, peer, variant=None) -> None:
        raise RuntimeError("boom")


class GatedListenerPackage(Installable):
    """Peer packages gated on the bootstrap framework."""

    name: str = "gated-listener"
    display_name: str = "Gated Listener"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="gated-extra", kind="pypi"),
        ]
    }


class SelfCleanListenerPackage(Installable):
    """No hooks, but owns peer packages gated on bootstrap."""

    name: str = "self-clean-listener"
    display_name: str = "Self Clean Listener"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="self-clean-extra", kind="pypi"),
        ]
    }


class RecursingListenerPackage(Installable):
    """A hook that triggers another integration sync (would loop without guard)."""

    name: str = "recursing-listener"
    display_name: str = "Recursing Listener"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="recursing-extra", kind="pypi"),
        ]
    }
    sync_kwargs: dict = {}

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))
        sync_on_add(FwPeer(), **self.sync_kwargs)


def make_registries(*classes) -> list[Registry]:
    registries_by_kind: dict = {}
    for cls in classes:
        kind = next(
            k
            for k in (PACKAGE, FRAMEWORK)
            if cls.model_fields["section"].default == k.section
        )
        registry = registries_by_kind.setdefault(kind, Registry(kind))
        registry.register(cls)
    return list(registries_by_kind.values())


# ── Ref matching (dataclass equality) ─────────────────────────────────────────


class TestMatching:
    def test_kind_must_match(self):
        interest = InstallableRef(name="bootstrap", kind=PACKAGE)
        assert interest != InstallableRef(name="bootstrap", kind=FRAMEWORK)

    def test_name_must_match(self):
        interest = InstallableRef(name="bootstrap", kind=FRAMEWORK)
        assert interest == InstallableRef(name="bootstrap", kind=FRAMEWORK)
        assert interest != InstallableRef(name="tailwind-cli", kind=FRAMEWORK)

    def test_ref_normalizes_underscores(self):
        interest = InstallableRef(kind=FRAMEWORK, name="tailwind_cli")
        assert interest.name == "tailwind-cli"
        assert interest == InstallableRef(kind=FRAMEWORK, name="tailwind-cli")


# ── Pull ───────────────────────────────────────────────────────────────────────


class TestPull:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_fires_when_peer_already_installed(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]

    def test_does_not_fire_when_peer_absent(self, root, pixi_ops):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []

    def test_fires_once_per_installed_variant(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap", variants=["account", "mfa"])

        class MultiVariantFw(FwPeer):
            variants: dict = {
                "account": Variant(name="account", display_name="Account"),
                "mfa": Variant(name="mfa", display_name="MFA"),
            }

        registries = make_registries(ListenerPackage, MultiVariantFw)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == [
            ("added", "bootstrap", "account"),
            ("added", "bootstrap", "mfa"),
        ]

    def test_unregistered_installed_peer_is_skipped_silently(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "ghost-framework")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []

    def test_named_interest_filters_peers(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "tailwind-cli")
        registries = make_registries(NamedListenerPackage, FwPeer, OtherFwPeer)

        sync_on_add(NamedListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []


# ── Push ───────────────────────────────────────────────────────────────────────


class TestPush:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_fires_when_listener_already_installed(self, root, pixi_ops):
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]

    def test_not_fired_for_non_installed_listeners(self, root, pixi_ops):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []

    def test_cross_category_framework_to_package(self, root, pixi_ops):
        """Push works across categories: framework add reaches package listener."""
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert ("added", "bootstrap", None) in CALLS

    def test_unregistered_installed_listener_is_skipped_silently(self, root, pixi_ops):
        track(root, Section.PACKAGES, "ghost-package")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []


# ── Remove / unwind ────────────────────────────────────────────────────────────


class TestUnwind:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_remove_triggers_on_peer_removed_on_installed_listeners(
        self, root, pixi_ops
    ):
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("removed", "bootstrap", None)]

    def test_variant_scoped_removal_passes_variant(self, root, pixi_ops):
        class MultiVariantFw(FwPeer):
            variants: dict = {
                "account": Variant(name="account", display_name="Account"),
                "mfa": Variant(name="mfa", display_name="MFA"),
            }

        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, MultiVariantFw)

        sync_on_remove(
            MultiVariantFw(),
            variant=MultiVariantFw().variants["mfa"],
            registries=registries,
            project_root=root,
        )

        assert CALLS == [("removed", "bootstrap", "mfa")]

    def test_no_unwind_for_non_installed_listeners(self, root, pixi_ops):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []


# ── Peer packages ──────────────────────────────────────────────────────────────


class GateOnlyPackage(Installable):
    """Reacts to bootstrap purely via peer_pixi_packages — no hooks."""

    name: str = "gate-only"
    display_name: str = "Gate Only"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="gate-only-extra", kind="pypi"),
        ]
    }


class HookedGatedPackage(Installable):
    """Declares peer packages and hooks for bootstrap."""

    name: str = "hooked-gated"
    display_name: str = "Hooked Gated"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="hooked-extra", kind="pypi"),
        ]
    }

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))


class TestPeerPackages:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_push_applies_peer_packages(self, root, pixi_ops):
        track(root, Section.PACKAGES, "gate-only")
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )

    def test_pull_applies_peer_for_peer_installed_earlier(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_add(GateOnlyPackage(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )

    def test_peer_unwinds_when_removed(self, root, pixi_ops):
        track(root, Section.PACKAGES, "gate-only")

        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )

    def test_hook_and_package_synced_together(self, root, pixi_ops):
        track(root, Section.PACKAGES, "hooked-gated")
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(HookedGatedPackage, FwPeer)

        sync_on_add(HookedGatedPackage(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]
        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="hooked-extra", kind="pypi")]
        )


# ── Partial variant removal ────────────────────────────────────────────────────


class GatedVariantOwner(Installable):
    name: str = "gated-variant-owner"
    display_name: str = "Gated Variant Owner"
    section: Section = Section.PACKAGES
    variants: dict[str, Variant] = {
        "alpha": Variant(name="alpha", display_name="Alpha"),
        "beta": Variant(name="beta", display_name="Beta"),
    }
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="owner-extra", kind="pypi"),
        ]
    }


class TestPartialVariantRemoval:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def seed(self, root: Path):
        track(
            root,
            Section.PACKAGES,
            "gated-variant-owner",
            variants=["alpha", "beta"],
        )

        return make_registries(GatedVariantOwner)

    def test_variant_removal_keeps_records_and_packages(self, root, pixi_ops):
        registries = self.seed(root)
        owner = GatedVariantOwner()

        sync_on_remove(
            owner,
            variant=owner.variants["beta"],
            registries=registries,
            project_root=root,
            fully_removed=False,
        )

        pixi_ops.remove_packages.assert_not_called()

    def test_full_removal_still_drops_records_and_packages(self, root, pixi_ops):
        registries = self.seed(root)

        sync_on_remove(
            GatedVariantOwner(),
            registries=registries,
            project_root=root,
            fully_removed=True,
        )

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="owner-extra", kind="pypi")]
        )

    @pytest.mark.parametrize(
        "installed_variants, expected",
        [(["alpha", "beta"], False), (["beta"], True)],
        ids=["partial", "last-variant"],
    )
    def test_installable_remove_passes_fully_removed(
        self, root, monkeypatch, installed_variants, expected
    ):
        received = {}

        def fake_sync(installable, variant=None, **kwargs):
            received["fully_removed"] = kwargs.get("fully_removed")

        monkeypatch.setattr("djdevx.installable.lifecycle.sync_on_remove", fake_sync)
        tracker = MagicMock()
        tracker.list.return_value = {}
        tracker.get_variants.return_value = installed_variants
        with (
            patch.object(PixiOps, "__init__", return_value=None),
            patch.object(PixiOps, "remove_packages"),
            patch.object(SecretsOps, "__init__", return_value=None),
            patch.object(SecretsOps, "remove"),
            patch("djdevx.installable.lifecycle.cleanup_files", MagicMock()),
            patch(
                "djdevx.installable.lifecycle.restore_original_templates",
                MagicMock(),
            ),
            patch(
                "djdevx.installable.lifecycle.ProjectStructure",
                **{"return_value.root": root},
            ),
            patch(
                "djdevx.installable.ops.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            GatedVariantOwner().remove(variant_name="beta")

        assert received["fully_removed"] is expected


# ── Error isolation ────────────────────────────────────────────────────────────


class TestErrorIsolation:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_raising_hook_is_caught_and_others_still_run(self, root, pixi_ops, capsys):
        track(root, Section.PACKAGES, "raising-listener")
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(RaisingListenerPackage, ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert ("added", "bootstrap", None) in CALLS
        assert "boom" in capsys.readouterr().out


# ── Recursion guard ────────────────────────────────────────────────────────────


class TestRecursionGuard:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_hook_triggered_sync_does_not_loop(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        track(root, Section.PACKAGES, "recursing-listener")
        registries = make_registries(RecursingListenerPackage, FwPeer)
        listener = RecursingListenerPackage(
            sync_kwargs={"registries": registries, "project_root": root}
        )

        sync_on_add(listener, registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]


# ── call_peer ──────────────────────────────────────────────────────────────────


class GreeterPackage(Installable):
    name: str = "greeter"
    display_name: str = "Greeter"
    section: Section = Section.PACKAGES

    def greet(self, greeting: str = "hello") -> str:
        return f"{greeting} from greeter"


class TestCallPeer:
    def test_returns_method_result(self, root, monkeypatch):
        monkeypatch.chdir(root)
        track(root, Section.PACKAGES, "greeter")

        result = call_peer(
            InstallableRef("greeter", PACKAGE),
            "greet",
            greeting="hi",
            registries=make_registries(GreeterPackage),
        )

        assert result == "hi from greeter"

    def test_default_when_peer_not_installed(self, root, monkeypatch):
        monkeypatch.chdir(root)

        result = call_peer(
            InstallableRef("greeter", PACKAGE),
            "greet",
            default="fallback",
            registries=make_registries(GreeterPackage),
        )

        assert result == "fallback"

    def test_default_when_peer_not_registered(self, root, monkeypatch):
        monkeypatch.chdir(root)
        track(root, Section.PACKAGES, "ghost")

        result = call_peer(
            InstallableRef("ghost", PACKAGE), "greet", default="fallback"
        )

        assert result == "fallback"


# ── Lifecycle wiring (end-to-end via CLI, both orders) ─────────────────────────


class TestLifecycleWiring:
    """Attach peer_pixi_packages to whitenoise at runtime and verify both orders fire."""

    @pytest.fixture
    def pixi_ops(self):
        with (
            patch("djdevx.installable.ops.pixi.PixiOps") as ops,
            patch("djdevx.installable.peers.PixiOps") as peer_ops,
            patch("djdevx.installable.lifecycle.PixiOps") as inst_ops,
        ):
            yield ops.return_value, peer_ops.return_value, inst_ops.return_value

    def _install_listening_whitenoise(self, monkeypatch) -> list[str]:
        calls: list[str] = []

        class ListeningWhitenoise(WhitenoisePackage):
            peer_pixi_packages: dict = {
                InstallableRef(name="bootstrap", kind=FRAMEWORK): [
                    PixiPackageSpec(name="whitenoise-extra", kind="pypi"),
                ]
            }

            def on_peer_added(self, peer, variant=None) -> None:
                calls.append(peer.name)

        monkeypatch.setitem(
            PACKAGE_REGISTRY._entries, "whitenoise", ListeningWhitenoise
        )
        return calls

    def test_framework_first_then_listener_pull(self, tmp_path, monkeypatch, pixi_ops):
        runner = CliRunner()
        create_test_django_project(tmp_path, runner)
        os.chdir(tmp_path)
        calls = self._install_listening_whitenoise(monkeypatch)

        result = runner.invoke(app, ["frameworks", "add", "bootstrap"])
        assert result.exit_code == 0, result.output
        assert calls == []

        result = runner.invoke(app, ["packages", "add", "whitenoise"])
        assert result.exit_code == 0, result.output
        assert calls == ["bootstrap"]

    def test_listener_first_then_framework_push(self, tmp_path, monkeypatch, pixi_ops):
        runner = CliRunner()
        create_test_django_project(tmp_path, runner)
        os.chdir(tmp_path)
        calls = self._install_listening_whitenoise(monkeypatch)

        result = runner.invoke(app, ["packages", "add", "whitenoise"])
        assert result.exit_code == 0, result.output
        assert calls == []

        result = runner.invoke(app, ["frameworks", "add", "bootstrap"])
        assert result.exit_code == 0, result.output
        assert calls == ["bootstrap"]


# ── Peer template cleanup ──────────────────────────────────────────────────────


class _TemplatePeer(Installable):
    name: str = "tpl-peer"
    display_name: str = "Template Peer"
    section: Section = Section.FRAMEWORKS

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tpl_dir = MagicMock()
        self._tpl_dir.exists.return_value = True
        self._tpl_dir.joinpath.return_value = self._tpl_dir
        self.template_dir = self._tpl_dir
        self.variants = {}
        self._install_context = {}


class TestPeerTemplateCleanup:
    def test_cleanup_removes_files_when_peer_dir_exists(self, root):
        listener = ListenerPackage()
        listener._install_context = {}
        listener._structure = MagicMock()
        listener._structure.root = root
        peer_tpl_dir = root / "peer_templates" / "peer_templates"
        peer_tpl_dir.mkdir(parents=True)
        (peer_tpl_dir / "style.css").write_text("body {}")
        (root / "style.css").write_text("body {}")

        class StubPeer(Installable):
            name: str = "stub-peer"
            display_name: str = "Stub Peer"
            section: Section = Section.FRAMEWORKS
            template_dir: ClassVar[Path] = root / "peer_templates"
            variants: dict = {}
            _install_context: dict = {}

        peer = StubPeer()

        with patch("djdevx.installable.peers.TemplateManager") as mock_tm_cls:
            mock_tm = MagicMock()
            mock_tm_cls.return_value = mock_tm
            mock_tm.scan_templates.return_value = ["style.css"]
            cleanup_peer_templates(listener, peer)

        assert not (root / "style.css").exists()

    def test_cleanup_noop_when_peer_dir_absent(self, root):
        listener = ListenerPackage()
        listener._install_context = {}
        listener._structure = MagicMock()
        listener._structure.root = root
        peer = _TemplatePeer()
        peer.template_dir = MagicMock()
        peer.template_dir.exists.return_value = False

        with patch("djdevx.installable.peers.TemplateManager"):
            cleanup_peer_templates(listener, peer)

    def test_cleanup_all_skips_unregistered_peers(self, root):
        """cleanup_all_peer_templates silently skips peers that are not registered."""
        listener = ListenerPackage()
        listener._install_context = {}
        listener._structure = MagicMock()
        listener._structure.root = root
        with (
            patch("djdevx.installable.peers.resolve", side_effect=KeyError),
            patch("djdevx.installable.peers.cleanup_peer_templates"),
        ):
            cleanup_all_peer_templates(listener)

    def test_copy_skips_when_peer_dir_absent(self, root):
        listener = ListenerPackage()
        listener._install_context = {}
        listener._structure = MagicMock()
        listener._structure.root = root
        peer = _TemplatePeer()
        peer.template_dir = MagicMock()
        peer.template_dir.exists.return_value = False
        with patch("djdevx.installable.peers.TemplateManager"):
            copy_peer_templates(listener, peer)


# ── Variant-scoped peer interest ───────────────────────────────────────────────


class VariantOnlyListener(Installable):
    """Declares peer interest only on a variant — no base-level packages."""

    name: str = "variant-only"
    display_name: str = "Variant Only"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {}
    variants: dict[str, Variant] = {
        "pro": Variant(
            name="pro",
            display_name="Pro",
            peer_pixi_packages={
                InstallableRef(name="bootstrap", kind=FRAMEWORK): [
                    PixiPackageSpec(name="pro-extra", kind="pypi"),
                ]
            },
        ),
    }

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, variant.name if variant else None))

    def on_peer_removed(self, peer, variant=None) -> None:
        CALLS.append(("removed", peer.name, variant.name if variant else None))


class VariantOwner(Installable):
    """Framework with two installed variants."""

    name: str = "multi-firmware"
    display_name: str = "Multi Firmware"
    section: Section = Section.FRAMEWORKS
    variants: dict[str, Variant] = {
        "account": Variant(name="account", display_name="Account"),
        "mfa": Variant(name="mfa", display_name="MFA"),
    }
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="fw-extra", kind="pypi"),
        ]
    }


def _seed_variant_tracking(root: Path, name: str, variants: list[str]) -> None:
    tracking = ProjectTracking(root)
    tracking.add(Section.PACKAGES, name, name.title(), variants=variants)


class TestVariantScopedInterest:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_pullof_variant_only_listener_adds_variant_package(self, root, pixi_ops):
        """PULL: listener with variant-only interest fires hook and adds package."""
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(VariantOnlyListener, FwPeer)
        listener = VariantOnlyListener()
        variant = listener.variants["pro"]

        sync_on_add(
            listener,
            registries=registries,
            variant=variant,
            project_root=root,
        )

        # Hook fires with peer variant (bootstrap has none), packages are variant-scoped
        assert CALLS == [("added", "bootstrap", None)]
        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="pro-extra", kind="pypi")]
        )

    def test_push_fires_variant_listener_for_each_installed_variant(
        self, root, pixi_ops
    ):
        """PUSH: listener with two installed variants fires hooks and adds packages for both."""
        _seed_variant_tracking(root, "variant-only", ["pro"])
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(VariantOnlyListener, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        # Hook fires once (bootstrap has no variants)
        assert CALLS == [("added", "bootstrap", None)]
        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="pro-extra", kind="pypi")]
        )

    def test_unwind_drops_variant_packages(self, root, pixi_ops):
        """UNWIND: removing peer drops packages for listener's installed variants."""
        _seed_variant_tracking(root, "variant-only", ["pro"])
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(VariantOnlyListener, FwPeer)

        # Pre-seed applied metadata for the peer package
        tracking = ProjectTracking(root)
        tracking.set_metadata(
            Section.PACKAGES,
            "variant-only",
            "peer_pixi_applied",
            ["pypi:pro-extra"],
        )

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("removed", "bootstrap", None)]
        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="pro-extra", kind="pypi")]
        )

    def test_idempotent_add_no_double_packages(self, root, pixi_ops):
        """Re-running add on an already-synced listener does not double-add packages."""
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GatedListenerPackage, FwPeer)

        sync_on_add(GatedListenerPackage(), registries=registries, project_root=root)
        pixi_ops.add_packages.reset_mock()

        sync_on_add(GatedListenerPackage(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_not_called()


# ── Hook-only listener ─────────────────────────────────────────────────────────


class HookOnlyListener(Installable):
    """Hook-only: peer_pixi_packages has a key with an empty list."""

    name: str = "hook-only"
    display_name: str = "Hook Only"
    section: Section = Section.PACKAGES
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [],
    }

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))

    def on_peer_removed(self, peer, variant=None) -> None:
        CALLS.append(("removed", peer.name, None))


class TestHookOnlyListener:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_hook_fires_without_any_packages_added(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(HookOnlyListener, FwPeer)

        sync_on_add(HookOnlyListener(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]
        pixi_ops.add_packages.assert_not_called()
        pixi_ops.remove_packages.assert_not_called()

    def test_unwind_fires_hook_and_no_packages_removed(self, root, pixi_ops):
        track(root, Section.PACKAGES, "hook-only")
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(HookOnlyListener, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("removed", "bootstrap", None)]
        pixi_ops.remove_packages.assert_not_called()
