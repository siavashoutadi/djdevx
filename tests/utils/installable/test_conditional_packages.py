"""Unit tests for ConditionalPackage — per-package `when` conditions."""

import pytest
from unittest.mock import MagicMock, patch

from djdevx.packages._base import BasePackage
from djdevx.utils.installable.pixi_ops import PixiOps
from djdevx.utils.installable.secrets import SecretsOps
from djdevx.utils.installable.types import ConditionalPackage, Variant
from djdevx.utils.types.pixi_types import PixiPackageSpec


class LambdaGatedPackage(BasePackage):
    name: str = "lambda-gated"
    display_name: str = "Lambda Gated"
    use_extra: bool = False
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="lambda-extra", kind="pypi"),
            when=lambda ctx: ctx.installable.use_extra,
        )
    ]


class MethodGatedPackage(BasePackage):
    name: str = "method-gated"
    display_name: str = "Method Gated"
    use_redis: bool = False

    def _needs_redis(ctx) -> bool:
        return ctx.installable.use_redis

    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="redis-extra", kind="pypi"),
            when=_needs_redis,
        )
    ]


class MixedGatedPackage(BasePackage):
    name: str = "mixed-gated"
    display_name: str = "Mixed Gated"
    flag_a: bool = True
    flag_b: bool = False
    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec(name="always-a", kind="pypi"),
            when=lambda ctx: ctx.installable.flag_a,
        ),
        ConditionalPackage(
            package=PixiPackageSpec(name="never-b", kind="pypi"),
            when=lambda ctx: ctx.installable.flag_b,
        ),
    ]


class VariantGatedPackage(BasePackage):
    name: str = "variant-gated"
    display_name: str = "Variant Gated"
    use_variant_extra: bool = False

    def _needs_variant_extra(ctx) -> bool:
        return ctx.installable.use_variant_extra

    variants: dict[str, Variant] = {
        "pro": Variant(
            name="pro",
            display_name="Pro",
            conditional_packages=[
                ConditionalPackage(
                    package=PixiPackageSpec(name="variant-extra", kind="pypi"),
                    when=_needs_variant_extra,
                ),
            ],
        ),
    }


def make_pkg(pkg_cls, **kwargs):
    pkg = pkg_cls(**kwargs)
    pkg._structure = MagicMock()
    pkg._structure.root = "/tmp/fake-root"
    return pkg


def _fake_tracking():
    tracker = MagicMock()
    tracker.list.return_value = {}
    tracker.get_variants.return_value = []
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
            **{"return_value.root": "/tmp/fake-root"},
        ),
        patch(
            "djdevx.utils.installable.peers.ProjectTracking",
            return_value=_fake_tracking(),
        ),
        patch("djdevx.utils.installable.tracking.ProjectTracking"),
    ):
        yield mock_add


class TestConditionalPackagesAdd:
    def test_true_condition_adds_package(self, add_mocks):
        pkg = make_pkg(LambdaGatedPackage, use_extra=True)
        pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="lambda-extra", kind="pypi") in flat

    def test_false_condition_skips_package(self, add_mocks):
        pkg = make_pkg(LambdaGatedPackage, use_extra=False)
        pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="lambda-extra", kind="pypi") not in flat

    def test_method_ref_when(self, add_mocks):
        pkg = make_pkg(MethodGatedPackage, use_redis=True)
        pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="redis-extra", kind="pypi") in flat

    def test_multiple_conditions_mixed(self, add_mocks):
        pkg = make_pkg(MixedGatedPackage)
        pkg.add()
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="always-a", kind="pypi") in flat
        assert PixiPackageSpec(name="never-b", kind="pypi") not in flat

    def test_variant_conditional_applied_via_parent_state(self, add_mocks):
        pkg = make_pkg(VariantGatedPackage, use_variant_extra=True)
        pkg.add(variant_name="pro")
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="variant-extra", kind="pypi") in flat

    def test_variant_conditional_skipped(self, add_mocks):
        pkg = make_pkg(VariantGatedPackage, use_variant_extra=False)
        pkg.add(variant_name="pro")
        calls = [c.args[0] for c in add_mocks.call_args_list]
        flat = [spec for call in calls for spec in call]
        assert PixiPackageSpec(name="variant-extra", kind="pypi") not in flat


class TestConditionalPackagesRemove:
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
                **{"return_value.root": "/tmp/fake-root"},
            ),
            patch(
                "djdevx.utils.installable.peers.ProjectTracking",
                return_value=_fake_tracking(),
            ),
            patch("djdevx.utils.installable.tracking.ProjectTracking"),
        ):
            yield mock_rem

    def _flat_specs(self, mock_rem):
        return [
            spec
            for c in mock_rem.call_args_list
            if c.args
            for spec in (c.args[0] if isinstance(c.args[0], list) else [c.args[0]])
        ]

    def test_remove_evaluates_condition(self, remove_mocks):
        pkg = make_pkg(LambdaGatedPackage, use_extra=True)
        pkg.remove()
        assert PixiPackageSpec(name="lambda-extra", kind="pypi") in self._flat_specs(
            remove_mocks
        )

    def test_remove_skips_false_condition(self, remove_mocks):
        pkg = make_pkg(LambdaGatedPackage, use_extra=False)
        pkg.remove()
        assert PixiPackageSpec(
            name="lambda-extra", kind="pypi"
        ) not in self._flat_specs(remove_mocks)
