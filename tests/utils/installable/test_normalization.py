"""Tests for name normalization at construction time.

Names containing underscores must be silently converted to hyphens the moment
an ``InstallableConfig`` subclass or ``InstallableRef`` is created.  No caller
should need to call ``normalize_name()`` manually after that point.
"""

import pytest

from djdevx.utils.installable.registry import Registry
from djdevx.utils.installable.types import (
    CACHE,
    DATABASE,
    FEATURE,
    FRAMEWORK,
    PACKAGE,
    InstallableConfig,
    InstallableKind,
    InstallableRef,
    Variant,
)


# ---------------------------------------------------------------------------
# InstallableConfig
# ---------------------------------------------------------------------------


class TestInstallableConfigNormalization:
    def test_underscore_converted_at_construction(self):
        cfg = InstallableConfig(name="my_package")
        assert cfg.name == "my-package"

    def test_hyphen_unchanged(self):
        cfg = InstallableConfig(name="my-package")
        assert cfg.name == "my-package"

    def test_multiple_underscores(self):
        cfg = InstallableConfig(name="open_telemetry_sdk")
        assert cfg.name == "open-telemetry-sdk"

    def test_name_already_valid(self):
        cfg = InstallableConfig(name="django")
        assert cfg.name == "django"

    def test_subclass_inherits_normalization_on_explicit_value(self):
        """Validator fires when a value is passed explicitly, even in a subclass."""

        class MyPkg(InstallableConfig):
            name: str = "my-pkg"

        assert MyPkg(name="my_pkg").name == "my-pkg"

    def test_subclass_class_level_default_not_run_through_validator(self):
        """Pydantic v2 does not run validators on field defaults.

        Convention: always write class-level ``name`` with hyphens so that
        ``MyPkg()`` and ``MyPkg.get_installable_name()`` both return the
        canonical form without relying on the validator.
        """

        class MyPkg(InstallableConfig):
            name: str = "my-pkg"  # hyphens by convention

        assert MyPkg().name == "my-pkg"


# ---------------------------------------------------------------------------
# Variant — underscores are converted like installable names
# ---------------------------------------------------------------------------


class TestVariantNameNormalization:
    def test_variant_underscore_converted(self):
        v = Variant(name="oidc_provider")
        assert v.name == "oidc-provider"

    def test_variant_hyphen_unchanged(self):
        v = Variant(name="brevo")
        assert v.name == "brevo"


# ---------------------------------------------------------------------------
# InstallableRef
# ---------------------------------------------------------------------------


class TestInstallableRefNormalization:
    def test_underscore_converted_at_construction(self):
        ref = InstallableRef(name="tailwind_cli", kind=FRAMEWORK)
        assert ref.name == "tailwind-cli"

    def test_hyphen_unchanged(self):
        ref = InstallableRef(name="tailwind-cli", kind=FRAMEWORK)
        assert ref.name == "tailwind-cli"

    def test_equality_across_underscore_and_hyphen(self):
        """A ref built with underscores must equal one built with hyphens."""
        assert InstallableRef("open_telemetry", FEATURE) == InstallableRef(
            "open-telemetry", FEATURE
        )

    def test_kind_still_differentiates_refs(self):
        assert InstallableRef("redis", PACKAGE) != InstallableRef("redis", CACHE)
        assert InstallableRef("postgres", DATABASE) != InstallableRef(
            "postgres", PACKAGE
        )

    @pytest.mark.parametrize(
        "kind",
        [PACKAGE, FEATURE, FRAMEWORK, DATABASE, CACHE],
        ids=["package", "feature", "framework", "database", "cache"],
    )
    def test_all_kinds_normalize(self, kind):
        ref = InstallableRef(name="some_thing", kind=kind)
        assert ref.name == "some-thing"

    def test_frozen_prevents_mutation(self):
        ref = InstallableRef(name="redis", kind=CACHE)
        with pytest.raises((AttributeError, TypeError)):
            ref.name = "memcached"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# get_installable_name class method
# ---------------------------------------------------------------------------


class TestGetInstallableName:
    def test_normalizes_class_level_name(self):
        class MyPkg(InstallableConfig):
            name: str = "my_pkg"

        assert MyPkg.get_installable_name() == "my-pkg"

    def test_already_hyphenated(self):
        class MyPkg(InstallableConfig):
            name: str = "my-pkg"

        assert MyPkg.get_installable_name() == "my-pkg"


# ---------------------------------------------------------------------------
# Registry lookup
# ---------------------------------------------------------------------------


class TestRegistryLookupNormalization:
    def test_get_accepts_underscores(self):
        class MyPkg(InstallableConfig):
            name: str = "my-pkg"

        registry: Registry[InstallableConfig] = Registry(
            InstallableKind("test-norm", PACKAGE.section)
        )
        registry.register(MyPkg)

        assert registry.get("my_pkg") is MyPkg
        assert registry.get("my-pkg") is MyPkg
