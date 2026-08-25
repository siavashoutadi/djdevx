"""Unit tests for the peer integration engine (utils/installable/peers.py)."""

import os
import tomllib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from djdevx.main import app
from djdevx.packages._registry import PACKAGE_REGISTRY
from djdevx.packages.whitenoise import WhitenoisePackage
from djdevx.utils.installable.peers import (
    call_peer,
    sync_on_add,
    sync_on_remove,
    when_peer,
)
from djdevx.utils.installable.installable import Installable
from djdevx.utils.installable.pixi_ops import PixiOps
from djdevx.utils.installable.registry import Registry
from djdevx.utils.installable.secrets import SecretsOps
from djdevx.utils.installable.types import (
    FRAMEWORK,
    PACKAGE,
    ConditionalPackage,
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


def extra_packages_in_toml(root: Path, section: Section, name: str):
    doc = tomllib.loads((root / "djdevx.toml").read_text())
    return doc.get(section.value, {}).get(name, {}).get("extra_packages")


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
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, variant.name if variant else None))

    def on_peer_removed(self, peer, variant=None) -> None:
        CALLS.append(("removed", peer.name, variant.name if variant else None))


class NamedListenerPackage(ListenerPackage):
    """Listens only to a specific framework (bootstrap)."""

    name: str = "named-listener"
    display_name: str = "Named Listener"
    listens_to: list[InstallableRef] = [
        InstallableRef(kind=FRAMEWORK, name="bootstrap")
    ]


class UninterestedPackage(Installable):
    name: str = "uninterested"
    display_name: str = "Uninterested"
    section: Section = Section.PACKAGES

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))


class RaisingListenerPackage(Installable):
    name: str = "raising-listener"
    display_name: str = "Raising Listener"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]

    def on_peer_added(self, peer, variant=None) -> None:
        raise RuntimeError("boom")


class GatedListenerPackage(Installable):
    """Conditional packages gated on the bootstrap framework."""

    name: str = "gated-listener"
    display_name: str = "Gated Listener"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="gated-extra", kind="pypi"),
            when=when_peer(InstallableRef("bootstrap", FRAMEWORK)),
        )
    ]


class SelfCleanListenerPackage(Installable):
    """No listens_to, but owns conditional packages gated on bootstrap."""

    name: str = "self-clean-listener"
    display_name: str = "Self Clean Listener"
    section: Section = Section.PACKAGES
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="self-clean-extra", kind="pypi"),
            when=when_peer(InstallableRef("bootstrap", FRAMEWORK)),
        )
    ]


class RecursingListenerPackage(Installable):
    """A hook that triggers another integration sync (would loop without guard)."""

    name: str = "recursing-listener"
    display_name: str = "Recursing Listener"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]
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
    def test_fires_when_peer_already_installed(self, root):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]

    def test_does_not_fire_when_peer_absent(self, root):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []

    def test_fires_once_per_installed_variant(self, root):
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

    def test_unregistered_installed_peer_is_skipped_silently(self, root):
        track(root, Section.FRAMEWORKS, "ghost-framework")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(ListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []

    def test_named_interest_filters_peers(self, root):
        track(root, Section.FRAMEWORKS, "tailwind-cli")
        registries = make_registries(NamedListenerPackage, FwPeer, OtherFwPeer)

        sync_on_add(NamedListenerPackage(), registries=registries, project_root=root)

        assert CALLS == []


# ── Push ───────────────────────────────────────────────────────────────────────


class TestPush:
    def test_fires_when_listener_already_installed(self, root):
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("added", "bootstrap", None)]

    def test_not_fired_for_non_installed_listeners(self, root):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []

    def test_cross_category_framework_to_package(self, root):
        """Push works across categories: framework add reaches package listener."""
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert ("added", "bootstrap", None) in CALLS

    def test_unregistered_installed_listener_is_skipped_silently(self, root):
        track(root, Section.PACKAGES, "ghost-package")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []


# ── Remove / unwind ────────────────────────────────────────────────────────────


class TestUnwind:
    def test_remove_triggers_on_peer_removed_on_installed_listeners(self, root):
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == [("removed", "bootstrap", None)]

    def test_variant_scoped_removal_passes_variant(self, root):
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

    def test_no_unwind_for_non_installed_listeners(self, root):
        registries = make_registries(ListenerPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        assert CALLS == []


# ── Implicit interest via when_peer gates ─────────────────────────────────────


class GateOnlyPackage(Installable):
    """Reacts to bootstrap purely via a when_peer gate — no listens_to."""

    name: str = "gate-only"
    display_name: str = "Gate Only"
    section: Section = Section.PACKAGES
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="gate-only-extra", kind="pypi"),
            when=when_peer(InstallableRef("bootstrap", FRAMEWORK)),
        )
    ]


class HookedGatedPackage(Installable):
    """Declares the same ref both ways — the hook must fire exactly once."""

    name: str = "hooked-gated"
    display_name: str = "Hooked Gated"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [InstallableRef("bootstrap", FRAMEWORK)]
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="hooked-extra", kind="pypi"),
            when=when_peer(InstallableRef("bootstrap", FRAMEWORK)),
        )
    ]

    def on_peer_added(self, peer, variant=None) -> None:
        CALLS.append(("added", peer.name, None))


class TestImplicitGateInterest:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.utils.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_push_applies_gate_without_listens_to(self, root, pixi_ops):
        # both sides tracked: sync runs after each side's own install
        track(root, Section.PACKAGES, "gate-only")
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )
        assert extra_packages_in_toml(root, Section.PACKAGES, "gate-only") == [
            "gate-only-extra"
        ]

    def test_pull_applies_gate_for_peer_installed_earlier(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_add(GateOnlyPackage(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )

    def test_gate_only_unwinds_when_peer_removed(self, root, pixi_ops):
        track(root, Section.PACKAGES, "gate-only")
        ProjectTracking(root).add(
            Section.PACKAGES,
            "gate-only",
            metadata={"extra_packages": ["gate-only-extra"]},
        )
        registries = make_registries(GateOnlyPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="gate-only-extra", kind="pypi")]
        )
        assert extra_packages_in_toml(root, Section.PACKAGES, "gate-only") == []

    def test_ref_declared_both_ways_fires_hook_once(self, root, pixi_ops):
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
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="owner-extra", kind="pypi"),
            when=lambda ctx: True,
        )
    ]


class TestPartialVariantRemoval:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.utils.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def seed(self, root: Path):
        track(
            root,
            Section.PACKAGES,
            "gated-variant-owner",
            variants=["alpha", "beta"],
        )
        ProjectTracking(root).add(
            Section.PACKAGES,
            "gated-variant-owner",
            metadata={"extra_packages": ["owner-extra"]},
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
        assert extra_packages_in_toml(
            root, Section.PACKAGES, "gated-variant-owner"
        ) == ["owner-extra"]

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
        assert (
            extra_packages_in_toml(root, Section.PACKAGES, "gated-variant-owner") == []
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

        monkeypatch.setattr(
            "djdevx.utils.installable.installable.sync_on_remove", fake_sync
        )
        tracker = MagicMock()
        tracker.list.return_value = {}
        tracker.get_variants.return_value = installed_variants
        with (
            patch.object(PixiOps, "__init__", return_value=None),
            patch.object(PixiOps, "remove_packages"),
            patch.object(SecretsOps, "__init__", return_value=None),
            patch.object(SecretsOps, "remove"),
            patch("djdevx.utils.installable.installable.cleanup_files", MagicMock()),
            patch(
                "djdevx.utils.installable.installable.restore_original_templates",
                MagicMock(),
            ),
            patch(
                "djdevx.utils.installable.installable.ProjectStructure",
                **{"return_value.root": root},
            ),
            patch(
                "djdevx.utils.installable.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            GatedVariantOwner().remove(variant_name="beta")

        assert received["fully_removed"] is expected


# ── Conditional packages ───────────────────────────────────────────────────────


class TestConditionalPackages:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.utils.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_added_on_integration_and_recorded_in_tracking(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(GatedListenerPackage, FwPeer)

        sync_on_add(GatedListenerPackage(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="gated-extra", kind="pypi")]
        )
        assert extra_packages_in_toml(root, Section.PACKAGES, "gated-listener") == [
            "gated-extra"
        ]

    def test_removed_on_unwind_and_cleared_from_tracking(self, root, pixi_ops):
        track(root, Section.PACKAGES, "gated-listener")
        ProjectTracking(root).add(
            Section.PACKAGES,
            "gated-listener",
            metadata={"extra_packages": ["gated-extra"]},
        )
        registries = make_registries(GatedListenerPackage, FwPeer)

        sync_on_remove(FwPeer(), registries=registries, project_root=root)

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="gated-extra", kind="pypi")]
        )
        assert extra_packages_in_toml(root, Section.PACKAGES, "gated-listener") == []

    def test_listener_self_cleanup_removes_gated_packages(self, root, pixi_ops):
        """Removing the listening side clears its own gated packages."""
        track(root, Section.FRAMEWORKS, "bootstrap")  # gate still installed
        track(root, Section.PACKAGES, "self-clean-listener")
        ProjectTracking(root).add(
            Section.PACKAGES,
            "self-clean-listener",
            metadata={"extra_packages": ["self-clean-extra"]},
        )
        registries = make_registries(SelfCleanListenerPackage, FwPeer)

        sync_on_remove(
            SelfCleanListenerPackage(), registries=registries, project_root=root
        )

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="self-clean-extra", kind="pypi")]
        )
        assert (
            extra_packages_in_toml(root, Section.PACKAGES, "self-clean-listener") == []
        )

    def test_self_cleanup_skips_gate_already_gone(self, root, pixi_ops):
        """When the gate was removed first, its unwind already handled cleanup."""
        registries = make_registries(SelfCleanListenerPackage, FwPeer)

        sync_on_remove(
            SelfCleanListenerPackage(), registries=registries, project_root=root
        )

        pixi_ops.remove_packages.assert_not_called()

    def test_not_added_when_gate_peer_absent(self, root, pixi_ops):
        registries = make_registries(GatedListenerPackage, FwPeer)

        sync_on_add(GatedListenerPackage(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_not_called()
        assert extra_packages_in_toml(root, Section.PACKAGES, "gated-listener") is None

    def test_unwind_skips_unrelated_peer_removal(self, root, pixi_ops):
        """Removing one framework must not unwind gates on another framework."""
        track(root, Section.FRAMEWORKS, "bootstrap")  # gate still installed
        track(root, Section.PACKAGES, "gated-listener")
        registries = make_registries(GatedListenerPackage, FwPeer, OtherFwPeer)

        sync_on_remove(OtherFwPeer(), registries=registries, project_root=root)

        pixi_ops.remove_packages.assert_not_called()


class ParamGatedPackage(Installable):
    """Custom condition driven by instance config (no peer context needed)."""

    name: str = "param-gated"
    display_name: str = "Param Gated"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]
    use_extras: bool = False
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="param-extra", kind="pypi"),
            when=lambda ctx: ctx.installable.use_extras,
        )
    ]


class CombinedConditionPackage(Installable):
    """Condition combining peer presence (state) with instance state."""

    name: str = "combined-condition"
    display_name: str = "Combined Condition"
    section: Section = Section.PACKAGES
    listens_to: list[InstallableRef] = [
        InstallableRef(name="bootstrap", kind=FRAMEWORK)
    ]
    require_flag: bool = True

    def _when_bootstrap_and_flag(ctx) -> bool:
        return ctx.installable.require_flag and ctx.project.is_installed(
            FRAMEWORK.section, "bootstrap"
        )

    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="combined-extra", kind="pypi"),
            when=_when_bootstrap_and_flag,
        )
    ]


class TestCustomConditions:
    @pytest.fixture
    def pixi_ops(self):
        with patch("djdevx.utils.installable.peers.PixiOps") as ops:
            yield ops.return_value

    def test_param_condition_true_applies_on_sync(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(ParamGatedPackage, FwPeer)

        sync_on_add(
            ParamGatedPackage(use_extras=True),
            registries=registries,
            project_root=root,
        )

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="param-extra", kind="pypi")]
        )

    def test_param_condition_false_skips_apply(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        registries = make_registries(ParamGatedPackage, FwPeer)

        sync_on_add(
            ParamGatedPackage(use_extras=False),
            registries=registries,
            project_root=root,
        )

        pixi_ops.add_packages.assert_not_called()

    def test_self_cleanup_drops_recorded_packages(self, root, pixi_ops):
        """Owner removal cleans up everything the engine recorded, gate or not."""
        track(root, Section.PACKAGES, "param-gated")
        ProjectTracking(root).add(
            Section.PACKAGES,
            "param-gated",
            metadata={"extra_packages": ["param-extra"]},
        )
        registries = make_registries(ParamGatedPackage)

        sync_on_remove(
            ParamGatedPackage(use_extras=False),
            registries=registries,
            project_root=root,
        )

        pixi_ops.remove_packages.assert_called_once_with(
            [PixiPackageSpec(name="param-extra", kind="pypi")]
        )
        assert extra_packages_in_toml(root, Section.PACKAGES, "param-gated") == []

    def test_self_cleanup_noop_without_records(self, root, pixi_ops):
        track(root, Section.PACKAGES, "param-gated")
        registries = make_registries(ParamGatedPackage)

        sync_on_remove(
            ParamGatedPackage(use_extras=True), registries=registries, project_root=root
        )

        pixi_ops.remove_packages.assert_not_called()

    def test_combined_condition_uses_peer_state(self, root, pixi_ops):
        track(root, Section.FRAMEWORKS, "bootstrap")
        track(root, Section.PACKAGES, "combined-condition")
        registries = make_registries(CombinedConditionPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_called_once_with(
            [PixiPackageSpec(name="combined-extra", kind="pypi")]
        )

    def test_combined_condition_false_without_peer(self, root, pixi_ops):
        track(root, Section.PACKAGES, "combined-condition")
        registries = make_registries(CombinedConditionPackage, OtherFwPeer)

        sync_on_add(OtherFwPeer(), registries=registries, project_root=root)

        pixi_ops.add_packages.assert_not_called()


# ── Error isolation ────────────────────────────────────────────────────────────


class TestErrorIsolation:
    def test_raising_hook_is_caught_and_others_still_run(self, root, capsys):
        track(root, Section.PACKAGES, "raising-listener")
        track(root, Section.PACKAGES, "listener")
        registries = make_registries(RaisingListenerPackage, ListenerPackage, FwPeer)

        sync_on_add(FwPeer(), registries=registries, project_root=root)

        assert ("added", "bootstrap", None) in CALLS
        assert "boom" in capsys.readouterr().out


# ── Recursion guard ────────────────────────────────────────────────────────────


class TestRecursionGuard:
    def test_hook_triggered_sync_does_not_loop(self, root):
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
    """Attach listens_to to whitenoise at runtime and verify both orders fire."""

    def _install_listening_whitenoise(self, monkeypatch) -> list[str]:
        calls: list[str] = []

        class ListeningWhitenoise(WhitenoisePackage):
            listens_to: list[InstallableRef] = [
                InstallableRef(name="bootstrap", kind=FRAMEWORK)
            ]

            def on_peer_added(self, peer, variant=None) -> None:
                calls.append(peer.name)

        monkeypatch.setitem(
            PACKAGE_REGISTRY._entries, "whitenoise", ListeningWhitenoise
        )
        return calls

    def test_framework_first_then_listener_pull(self, tmp_path, monkeypatch):
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

    def test_listener_first_then_framework_push(self, tmp_path, monkeypatch):
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
