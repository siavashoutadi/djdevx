"""Unit tests for peer_pixi_packages — peer-scoped dependency declarations."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from djdevx.providers.packages._base import BasePackage
from djdevx.utils.installable.pixi_ops import PixiOps
from djdevx.utils.installable.secrets import SecretsOps
from djdevx.utils.installable.types import DATABASE, FRAMEWORK, InstallableRef, Variant
from djdevx.utils.tracking.sections import Section
from djdevx.utils.types.pixi_types import PixiPackageSpec


class _DummyPeer:
    name: str = "bootstrap"
    display_name: str = "Bootstrap"

    def __init__(self, name: str = "bootstrap"):
        self.name = name
        self.template_dir = MagicMock()
        self.template_dir.exists.return_value = False
        self.variants = {}

    @classmethod
    def get_registry(cls):
        return None


class PeerGatedPackage(BasePackage):
    name: str = "peer-gated"
    display_name: str = "Peer Gated"
    peer_pixi_packages: dict = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="peer-extra", kind="pypi"),
        ]
    }


class MultiPeerPackage(BasePackage):
    name: str = "multi-peer"
    display_name: str = "Multi Peer"
    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="bootstrap-extra", kind="pypi"),
        ],
        InstallableRef(name="postgres", kind=DATABASE): [
            PixiPackageSpec(name="postgres-extra", kind="pypi"),
        ],
    }


class VariantPeerPackage(BasePackage):
    name: str = "variant-peer"
    display_name: str = "Variant Peer"
    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        InstallableRef(name="bootstrap", kind=FRAMEWORK): [
            PixiPackageSpec(name="owner-extra", kind="pypi"),
        ]
    }
    variants: dict[str, Variant] = {
        "pro": Variant(
            name="pro",
            display_name="Pro",
            peer_pixi_packages={
                InstallableRef(name="bootstrap", kind=FRAMEWORK): [
                    PixiPackageSpec(name="variant-extra", kind="pypi"),
                ]
            },
        ),
    }


def make_pkg(pkg_cls, **kwargs):
    pkg = pkg_cls(**kwargs)
    pkg._structure = MagicMock()
    pkg._structure.root = Path("/tmp/fake-root")
    return pkg


def _fake_tracking(installed=None, metadata=None):
    tracker = MagicMock()
    # The real ProjectTracking.list(section) returns {name: {metadata...}}
    # where name is the installable name, not the section name.
    tracker.list.return_value = {
        name: {"installed": True} for name in (installed or [])
    }
    tracker._metadata = metadata or {}

    def is_installed(section, name):
        section_list = tracker.list.return_value
        return name in section_list

    def get_metadata(section, name, key, default=None):
        return tracker._metadata.get((section, name, key), default)

    def set_metadata(section, name, key, value):
        tracker._metadata[(section, name, key)] = value

    def get_applied_peers(section, name):
        return tracker._metadata.get((section, name, "peer_pixi_applied"), set())

    def set_applied_peers(section, name, keys):
        tracker._metadata[(section, name, "peer_pixi_applied")] = keys

    tracker.is_installed = is_installed
    tracker.get_metadata = get_metadata
    tracker.set_metadata = set_metadata
    tracker.get_applied_peers = get_applied_peers
    tracker.set_applied_peers = set_applied_peers
    return tracker


@pytest.fixture
def add_mocks():
    with (
        patch.object(PixiOps, "__init__", return_value=None),
        patch.object(PixiOps, "add_packages") as mock_add,
        patch("djdevx.utils.installable.installable.copy_templates", MagicMock()),
        patch("djdevx.utils.installable.installable.format_files", MagicMock()),
        patch.object(SecretsOps, "generate", MagicMock()),
        patch.object(SecretsOps, "__init__", return_value=None),
        patch(
            "djdevx.utils.installable.peers.ProjectStructure",
            **{"return_value.root": Path("/tmp/fake-root")},
        ),
        patch(
            "djdevx.utils.installable.peers.ProjectTracking",
            return_value=_fake_tracking(),
        ),
        patch("djdevx.utils.installable.tracking.ProjectTracking"),
        patch(
            "djdevx.utils.installable.peers.resolve",
            return_value=_DummyPeer,
        ),
        patch(
            "djdevx.utils.installable.peers.get_section",
            return_value=Section.FRAMEWORKS,
        ),
    ):
        yield mock_add


class TestPeerPackagesAdd:
    def test_peer_installed_adds_package(self, add_mocks):
        tracker = _fake_tracking(["bootstrap"])
        with (
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            pkg = make_pkg(PeerGatedPackage)
            pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="peer-extra", kind="pypi") in flat

    def test_peer_not_installed_skips_package(self, add_mocks):
        pkg = make_pkg(PeerGatedPackage)
        pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="peer-extra", kind="pypi") not in flat

    def test_multiple_peers_adds_matching(self, add_mocks):
        tracker = _fake_tracking(["bootstrap"])
        with (
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            pkg = make_pkg(MultiPeerPackage)
            pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="bootstrap-extra", kind="pypi") in flat
        assert PixiPackageSpec(name="postgres-extra", kind="pypi") not in flat

    def test_variant_peer_package_applied(self, add_mocks):
        tracker = _fake_tracking(["bootstrap"])
        with (
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            pkg = make_pkg(VariantPeerPackage)
            pkg.add(variant_name="pro")
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        names = [s.name for s in flat]
        assert "owner-extra" in names
        assert "variant-extra" in names


class TestPeerPackagesRemove:
    @pytest.fixture
    def remove_mocks(self):
        with (
            patch.object(PixiOps, "__init__", return_value=None),
            patch.object(PixiOps, "remove_packages") as mock_rem,
            patch("djdevx.utils.installable.installable.cleanup_files", MagicMock()),
            patch(
                "djdevx.utils.installable.installable.restore_original_templates",
                MagicMock(),
            ),
            patch.object(SecretsOps, "remove", MagicMock()),
            patch.object(SecretsOps, "__init__", return_value=None),
            patch(
                "djdevx.utils.installable.peers.ProjectStructure",
                **{"return_value.root": Path("/tmp/fake-root")},
            ),
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=_fake_tracking(),
            ),
            patch("djdevx.utils.installable.tracking.ProjectTracking"),
            patch(
                "djdevx.utils.installable.peers.resolve",
                return_value=_DummyPeer,
            ),
            patch(
                "djdevx.utils.installable.peers.get_section",
                return_value=Section.FRAMEWORKS,
            ),
        ):
            yield mock_rem

    def _flat_specs(self, mock_rem):
        return [
            spec
            for c in mock_rem.call_args_list
            if c.args
            for spec in (c.args[0] if isinstance(c.args[0], list) else [c.args[0]])
        ]

    def test_remove_drops_peer_package(self, remove_mocks):
        tracker = _fake_tracking(["bootstrap"])
        # Seed the metadata to simulate that the peer package was applied
        tracker.set_metadata(
            Section.PACKAGES, "peer-gated", "peer_pixi_applied", ["pypi:peer-extra"]
        )
        with (
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.tracking.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.installable.installable.ProjectTracking",
                return_value=tracker,
            ),
        ):
            pkg = make_pkg(PeerGatedPackage)
            pkg.remove()
        # After remove, sync_on_remove removes the applied package via self-cleanup
        assert PixiPackageSpec(name="peer-extra", kind="pypi") in self._flat_specs(
            remove_mocks
        )

    def test_remove_skips_when_peer_gone(self, remove_mocks):
        pkg = make_pkg(PeerGatedPackage)
        pkg.remove()
        assert PixiPackageSpec(name="peer-extra", kind="pypi") not in self._flat_specs(
            remove_mocks
        )

    def test_stale_metadata_is_cleaned_up(self, add_mocks):
        """A stale identity key in metadata that no longer matches any declared
        spec should not crash; it is silently dropped on the next sync."""
        from djdevx.utils.installable.peers import _spec_key

        tracker = _fake_tracking(["bootstrap"])
        tracker.set_applied_peers(
            Section.PACKAGES,
            "peer-gated",
            {_spec_key(PixiPackageSpec(name="ghost-extra", kind="pypi"))},
        )
        with (
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=tracker,
            ),
            patch(
                "djdevx.utils.tracking.ProjectTracking",
                return_value=tracker,
            ),
        ):
            pkg = make_pkg(PeerGatedPackage)
            pkg.add()
        # No exception, and no ghost package should be added or removed.
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert all(s.name != "ghost-extra" for s in flat)
