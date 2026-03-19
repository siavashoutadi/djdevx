"""
Unit tests that verify the tracking config.toml written for each Django package
matches the expected fixture under data/<slug>/.djdevx/...
"""

import importlib
from pathlib import Path
from unittest.mock import patch


from djdevx.backend.django.packages._base import BasePackage

DATA_DIR = Path(__file__).parent / "data"


def _get_pkg(module_path: str) -> BasePackage:
    """Return the module-level _pkg singleton from a package module."""
    return importlib.import_module(module_path)._pkg


def _assert_tracking_config(pkg: BasePackage, data_slug: str, tmp_path: Path) -> None:
    """
    Write tracking config for *pkg* under *tmp_path* and compare it
    against the fixture file at data/<data_slug>/.djdevx/.../<template_path>/config.toml.
    """
    djdevx_root = tmp_path / ".djdevx"

    with patch(
        "djdevx.utils.djdevx_config.backend.package_tracker.ProjectConfig.djdevx_root",
        new_callable=lambda: property(lambda self: djdevx_root),
    ):
        pkg._write_package_tracking()
        pkg._write_env_tracking()

    actual_path = (
        djdevx_root
        / "backend"
        / "django"
        / "packages"
        / pkg._template_path
        / "config.toml"
    )
    expected_path = (
        DATA_DIR
        / data_slug
        / ".djdevx"
        / "backend"
        / "django"
        / "packages"
        / pkg._template_path
        / "config.toml"
    )

    assert actual_path.exists(), f"config.toml was not created at {actual_path}"
    assert expected_path.exists(), f"Expected fixture missing at {expected_path}"
    assert actual_path.read_text() == expected_path.read_text(), (
        f"Tracking config mismatch for {pkg._template_path}.\n"
        f"Expected:\n{expected_path.read_text()}\n"
        f"Got:\n{actual_path.read_text()}"
    )


# ---------------------------------------------------------------------------
# Flat packages
# ---------------------------------------------------------------------------


class TestFlatPackageTracking:
    """Tracking config tests for packages directly under packages/."""

    def test_whitenoise(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.whitenoise")
        _assert_tracking_config(pkg, "whitenoise", tmp_path)

    def test_channels(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.channels")
        _assert_tracking_config(pkg, "channels", tmp_path)

    def test_django_auditlog(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_auditlog")
        _assert_tracking_config(pkg, "django-auditlog", tmp_path)

    def test_django_browser_reload(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_browser_reload")
        _assert_tracking_config(pkg, "django-browser-reload", tmp_path)

    def test_django_cors_headers(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_cors_headers")
        _assert_tracking_config(pkg, "django-cors-headers", tmp_path)

    def test_django_csp(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_csp")
        _assert_tracking_config(pkg, "django-csp", tmp_path)

    def test_django_debug_toolbar(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_debug_toolbar")
        _assert_tracking_config(pkg, "django-debug-toolbar", tmp_path)

    def test_django_defender(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_defender")
        _assert_tracking_config(pkg, "django-defender", tmp_path)

    def test_django_extensions(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_extensions")
        _assert_tracking_config(pkg, "django-extensions", tmp_path)

    def test_django_filter(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_filter")
        _assert_tracking_config(pkg, "django-filter", tmp_path)

    def test_django_guardian(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_guardian")
        _assert_tracking_config(pkg, "django-guardian", tmp_path)

    def test_django_health_check(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_health_check")
        _assert_tracking_config(pkg, "django-health-check", tmp_path)

    def test_django_htmx(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_htmx")
        _assert_tracking_config(pkg, "django-htmx", tmp_path)

    def test_django_import_export(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_import_export")
        _assert_tracking_config(pkg, "django-import-export", tmp_path)

    def test_django_meta(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_meta")
        _assert_tracking_config(pkg, "django-meta", tmp_path)

    def test_django_oauth_toolkit(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_oauth_toolkit")
        _assert_tracking_config(pkg, "django-oauth-toolkit", tmp_path)

    def test_django_permissions_policy(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_permissions_policy")
        _assert_tracking_config(pkg, "django-permissions-policy", tmp_path)

    def test_django_role_permissions(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_role_permissions")
        _assert_tracking_config(pkg, "django-role-permissions", tmp_path)

    def test_django_silk(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_silk")
        _assert_tracking_config(pkg, "django-silk", tmp_path)

    def test_django_simple_history(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_simple_history")
        _assert_tracking_config(pkg, "django-simple-history", tmp_path)

    def test_django_simple_nav(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_simple_nav")
        _assert_tracking_config(pkg, "django-simple-nav", tmp_path)

    def test_django_snakeoil(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_snakeoil")
        _assert_tracking_config(pkg, "django-snakeoil", tmp_path)

    def test_django_taggit(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_taggit")
        _assert_tracking_config(pkg, "django-taggit", tmp_path)

    def test_django_tailwind_cli(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_tailwind_cli")
        _assert_tracking_config(pkg, "django_tailwind_cli", tmp_path)

    def test_djangochannelsrestframework(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.djangochannelsrestframework")
        _assert_tracking_config(pkg, "djangochannelsrestframework", tmp_path)

    def test_djangorestframework(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.djangorestframework")
        _assert_tracking_config(pkg, "djangorestframework", tmp_path)

    def test_drf_flex_fields(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.drf_flex_fields")
        _assert_tracking_config(pkg, "drf-flex-fields", tmp_path)

    def test_drf_nested_routers(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.drf_nested_routers")
        _assert_tracking_config(pkg, "drf-nested-routers", tmp_path)

    def test_drf_spectacular(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.drf_spectacular")
        _assert_tracking_config(pkg, "drf-spectacular", tmp_path)

    def test_heroicons(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.heroicons")
        _assert_tracking_config(pkg, "heroicons", tmp_path)


# ---------------------------------------------------------------------------
# django_allauth sub-packages
# ---------------------------------------------------------------------------


class TestDjangoAllauthTracking:
    """Tracking config tests for django_allauth sub-packages."""

    def test_account(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_allauth.account")
        _assert_tracking_config(pkg, "django_allauth", tmp_path)

    def test_mfa(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_allauth.mfa")
        _assert_tracking_config(pkg, "django_allauth", tmp_path)

    def test_oidc_provider(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_allauth.oidc_provider")
        _assert_tracking_config(pkg, "django_allauth", tmp_path)


# ---------------------------------------------------------------------------
# django_anymail sub-packages
# ---------------------------------------------------------------------------


class TestDjangoAnyMailTracking:
    """Tracking config tests for django_anymail provider sub-packages."""

    def test_brevo(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_anymail.brevo")
        _assert_tracking_config(pkg, "django_anymail", tmp_path)

    def test_mailgun(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_anymail.mailgun")
        _assert_tracking_config(pkg, "django_anymail", tmp_path)

    def test_mailjet(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_anymail.mailjet")
        _assert_tracking_config(pkg, "django_anymail", tmp_path)

    def test_resend(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_anymail.resend")
        _assert_tracking_config(pkg, "django_anymail", tmp_path)

    def test_ses(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_anymail.ses")
        _assert_tracking_config(pkg, "django_anymail", tmp_path)


# ---------------------------------------------------------------------------
# django_storages sub-packages
# ---------------------------------------------------------------------------


class TestDjangoStoragesTracking:
    """Tracking config tests for django_storages backend sub-packages."""

    def test_s3(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_storages.s3")
        _assert_tracking_config(pkg, "django_storages", tmp_path)

    def test_azure(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_storages.azure")
        _assert_tracking_config(pkg, "django_storages", tmp_path)

    def test_google(self, tmp_path):
        pkg = _get_pkg("djdevx.backend.django.packages.django_storages.google")
        _assert_tracking_config(pkg, "django_storages", tmp_path)
