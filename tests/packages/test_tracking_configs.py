"""
Unit tests for tracking via [packages] in djdevx.toml.
"""

from pathlib import Path
from unittest.mock import MagicMock

import tomlkit

from djdevx.providers.packages._base import BasePackage
from djdevx.utils.installable.tracking import TrackingOps
from djdevx.utils.installable.types import Variant
from djdevx.utils.tracking import ProjectTracking, Section
from djdevx.utils.types.pixi_types import PixiPackageSpec


class SimplePackage(BasePackage):
    name: str = "whitenoise"
    display_name: str = "Whitenoise"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="whitenoise", kind="pypi")
    ]


class VariantPackage(BasePackage):
    name: str = "sanctr"
    display_name: str = "Sanctr"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec(name="sanctr", kind="pypi")]
    variants: dict[str, Variant] = {
        "base": Variant(
            name="base",
            display_name="Base",
            pixi_packages=[PixiPackageSpec(name="sanctr-base", kind="pypi")],
            template_path="base",
        ),
    }


def setup_djdevx_toml(path: Path) -> Path:
    djdevx = path / "djdevx.toml"
    djdevx.write_text('project_name = "test"\n')
    return djdevx


class TestFlatPackageTracking:
    def test_write_creates_section(self, tmp_path):
        setup_djdevx_toml(tmp_path)
        pkg = SimplePackage()
        TrackingOps(Section.PACKAGES, tmp_path).track_install(pkg)
        doc = tomlkit.loads((tmp_path / "djdevx.toml").read_text())
        packages = doc.get("packages", {})
        assert "whitenoise" in packages
        assert packages["whitenoise"]["display_name"] == "Whitenoise"

    def test_write_creates_variant_section(self, tmp_path):
        setup_djdevx_toml(tmp_path)
        mock_project = MagicMock()
        mock_project.get_variants.return_value = []
        ops = TrackingOps(Section.PACKAGES, tmp_path)
        ops._project = mock_project
        pkg = VariantPackage()
        variant = pkg.variants["base"]
        ops.track_install(pkg, variant)
        mock_project.add.assert_called_once_with(
            Section.PACKAGES, "sanctr", "Sanctr", variants=["base"]
        )

    def test_read_after_write(self, tmp_path):
        setup_djdevx_toml(tmp_path)
        tracking = ProjectTracking(tmp_path)
        tracking.add(Section.PACKAGES, "whitenoise", "Whitenoise")
        installed = tracking.list(Section.PACKAGES)
        assert "whitenoise" in installed
        assert installed["whitenoise"]["display_name"] == "Whitenoise"

    def test_remove_tracking(self, tmp_path):
        setup_djdevx_toml(tmp_path)
        tracking = ProjectTracking(tmp_path)
        tracking.add(Section.PACKAGES, "whitenoise", "Whitenoise")
        assert tracking.is_installed(Section.PACKAGES, "whitenoise")
        tracking.remove(Section.PACKAGES, "whitenoise")
        assert not tracking.is_installed(Section.PACKAGES, "whitenoise")

    def test_is_installed_false_for_missing(self, tmp_path):
        setup_djdevx_toml(tmp_path)
        tracking = ProjectTracking(tmp_path)
        assert not tracking.is_installed(Section.PACKAGES, "nonexistent")

    def test_missing_djdevx_toml_creates_it(self, tmp_path):
        tracking = ProjectTracking(tmp_path)
        tracking.add(Section.PACKAGES, "heroicons", "Heroicons")
        doc = tomlkit.loads((tmp_path / "djdevx.toml").read_text())
        assert "heroicons" in doc["packages"]
