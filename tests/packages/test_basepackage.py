"""Unit tests for BasePackage — new flat architecture."""

from unittest.mock import MagicMock, patch

from djdevx.packages._base import BasePackage
from djdevx.utils.installable.pixi_ops import PixiOps
from djdevx.utils.installable.scaffold import cleanup_files, restore_original_templates
from djdevx.utils.installable.secrets import SecretsOps
from djdevx.utils.installable.tracking import track_install
from djdevx.utils.installable.types import (
    InstallParam,
    Variant,
)
from djdevx.utils.types.pixi_types import PixiPackageSpec


class SimplePackage(BasePackage):
    name: str = "simple"
    display_name: str = "Simple Package"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="simple-pkg", kind="pypi")
    ]


class VariantPackage(BasePackage):
    name: str = "variant-pkg"
    display_name: str = "Variant Package"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="variant-base", kind="pypi")
    ]
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "alpha": Variant(
            name="alpha",
            display_name="Alpha",
            pixi_packages=[PixiPackageSpec(name="variant-alpha", kind="pypi")],
        ),
        "beta": Variant(
            name="beta",
            display_name="Beta",
            pixi_packages=[PixiPackageSpec(name="variant-beta", kind="pypi")],
        ),
    }


class AdditiveVariantPackage(BasePackage):
    name: str = "additive-pkg"
    display_name: str = "Additive Package"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="additive-base", kind="pypi")
    ]
    exclusive_variants: bool = False
    variants: dict[str, Variant] = {
        "account": Variant(
            name="account",
            display_name="Account",
            required=True,
            pixi_packages=[PixiPackageSpec(name="additive-account", kind="pypi")],
        ),
        "mfa": Variant(
            name="mfa",
            display_name="MFA",
            pixi_packages=[PixiPackageSpec(name="additive-mfa", kind="pypi")],
        ),
    }


class CleanupPackage(BasePackage):
    name: str = "cleanup-pkg"
    display_name: str = "Cleanup Package"
    files_to_remove: list[str] = ["cleanup.txt", "subdir/nested.txt"]
    folders_to_remove: list[str] = ["cleanup_dir"]


class OverridePackage(BasePackage):
    name: str = "override-pkg"
    display_name: str = "Override Package"
    restore_on_remove: dict[str, str] = {"applications/asgi.py": "applications/asgi.py"}


class TestHookOrdering:
    def test_add_hook_order(self):
        call_order = []

        class TestPkg(SimplePackage):
            def model_post_init(self, __context):
                self._structure = MagicMock()
                self._pixi = MagicMock()
                self._tracking = MagicMock()

            def before_pixi_install(self):
                call_order.append("before_pixi_install")

            def after_pixi_install(self):
                call_order.append("after_pixi_install")

            def before_copy_templates(self):
                call_order.append("before_copy")

            def after_copy_templates(self):
                call_order.append("after_copy")

        with (
            patch.object(PixiOps, "add_packages") as mock_add,
            patch("djdevx.utils.installable.installable.copy_templates") as mock_copy,
            patch.object(SecretsOps, "generate") as mock_gen,
            patch("djdevx.utils.installable.tracking.SectionTracking"),
        ):
            mock_add.side_effect = lambda *a, **kw: call_order.append("pixi_add_all")
            mock_copy.side_effect = lambda self, variant: call_order.append(
                "copy_templates"
            )
            mock_gen.side_effect = lambda installable, variant: call_order.append(
                "gen_secrets"
            )
            TestPkg().add()
        assert call_order == [
            "before_pixi_install",
            "pixi_add_all",
            "after_pixi_install",
            "before_copy",
            "copy_templates",
            "after_copy",
            "gen_secrets",
        ]

    def test_remove_hook_order(self):
        call_order = []

        class TestPkg(SimplePackage):
            def model_post_init(self, __context):
                self._structure = MagicMock()

            def before_pixi_remove(self):
                call_order.append("before_pixi_remove")

            def after_pixi_remove(self):
                call_order.append("after_pixi_remove")

        with (
            patch.object(PixiOps, "remove_packages") as mock_rem_pixi,
            patch("djdevx.utils.installable.installable.cleanup_files") as mock_cleanup,
            patch(
                "djdevx.utils.installable.installable.restore_original_templates"
            ) as mock_restore,
            patch.object(SecretsOps, "remove") as mock_rem,
            patch("djdevx.utils.installable.tracking.SectionTracking"),
        ):
            mock_rem_pixi.side_effect = lambda *a, **kw: call_order.append(
                "pixi_remove_all"
            )
            mock_cleanup.side_effect = lambda self, variant: call_order.append(
                "cleanup_files"
            )
            mock_restore.side_effect = lambda self: call_order.append(
                "restore_overrides"
            )
            mock_rem.side_effect = lambda installable, variant: call_order.append(
                "remove_secrets"
            )
            TestPkg().remove()
        assert call_order == [
            "before_pixi_remove",
            "pixi_remove_all",
            "after_pixi_remove",
            "cleanup_files",
            "remove_secrets",
            "restore_overrides",
        ]


class TestCleanupExtraFiles:
    def test_removes_files(self, tmp_path):
        pkg = CleanupPackage()
        pkg._structure = MagicMock()
        pkg._structure.root = tmp_path
        (tmp_path / "cleanup.txt").write_text("x")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").write_text("y")
        cleanup_files(pkg)
        assert not (tmp_path / "cleanup.txt").exists()
        assert not (tmp_path / "subdir" / "nested.txt").exists()

    def test_removes_folders(self, tmp_path):
        pkg = CleanupPackage()
        pkg._structure = MagicMock()
        pkg._structure.root = tmp_path
        (tmp_path / "cleanup_dir").mkdir()
        (tmp_path / "cleanup_dir" / "file.txt").write_text("content")
        cleanup_files(pkg)
        assert not (tmp_path / "cleanup_dir").exists()

    def test_missing_ok(self, tmp_path):
        pkg = CleanupPackage()
        pkg._structure = MagicMock()
        pkg._structure.root = tmp_path
        cleanup_files(pkg)


class TestPackageTracking:
    def test_write_tracking_adds_to_djdevx_toml(self):
        pkg = SimplePackage()
        mock_tracking = MagicMock()
        with patch(
            "djdevx.utils.installable.tracking.SectionTracking",
            return_value=mock_tracking,
        ):
            track_install(pkg)
        mock_tracking.add.assert_called_once_with("simple", "Simple Package")

    def test_write_tracking_variant_appends(self):
        pkg = AdditiveVariantPackage()
        mock_tracking = MagicMock()
        mock_tracking.get_variants.return_value = ["account"]
        variant = pkg.variants["mfa"]
        with patch(
            "djdevx.utils.installable.tracking.SectionTracking",
            return_value=mock_tracking,
        ):
            track_install(pkg, variant)
        mock_tracking.add.assert_called_once_with(
            "additive-pkg", "Additive Package", variants=["account", "mfa"]
        )


class TestRestoreOverrides:
    def test_restores_from_new_templates(self, tmp_path):
        pkg = OverridePackage()
        pkg._structure = MagicMock()
        pkg._structure.root = tmp_path
        new_templates_dir = tmp_path / "new_templates"
        new_templates_dir.mkdir()
        (new_templates_dir / "applications").mkdir()
        (new_templates_dir / "applications" / "asgi.py").write_text(
            "# canonical asgi\n"
        )
        with patch.object(
            type(pkg),
            "new_templates_dir",
            new_callable=lambda: property(lambda self: new_templates_dir),
        ):
            restore_original_templates(pkg)
        dest = tmp_path / "applications" / "asgi.py"
        assert dest.exists()
        assert dest.read_text() == "# canonical asgi\n"


class TestVariant:
    def test_variant_defaults(self):
        v = Variant(name="test", display_name="Test")
        assert v.required is False
        assert v.pixi_packages == []
        assert v.template_path == ""

    def test_variant_with_values(self):
        v = Variant(
            name="brevo",
            display_name="Brevo",
            pixi_packages=[PixiPackageSpec(name="django-anymail[brevo]", kind="pypi")],
            template_path="brevo",
        )
        assert v.name == "brevo"
        assert v.pixi_packages == [
            PixiPackageSpec(name="django-anymail[brevo]", kind="pypi")
        ]


class TestInstallParam:
    def test_param_defaults(self):
        p = InstallParam(name="test")
        assert p.type_ is str
        assert p.default == ""
        assert p.prompt is None

    def test_param_with_values(self):
        p = InstallParam(
            name="color",
            type_=str,
            default="red",
            help="A color",
            prompt="Pick a color",
        )
        assert p.name == "color"
        assert p.default == "red"
        assert p.prompt == "Pick a color"
