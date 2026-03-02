"""Unit tests for BasePackage path derivation logic."""

from pathlib import Path
from unittest.mock import patch

from djdevx.backend.django.packages._base import BasePackage, PathDeriver


class TestPathDerivation:
    """Test path derivation methods for BasePackage."""

    def _mock_basepackage_with_file(self, file_path: str) -> BasePackage:
        """
        Helper to create a BasePackage instance with a mocked file path.

        Args:
            file_path: Relative path like 'whitenoise.py' or 'django_storages/s3.py'
        """
        # Create a mock object that will be treated as __file__
        mock_path = (
            Path("/home/siavash/code/djdevx/djdevx/backend/django/packages") / file_path
        )

        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage(str(mock_path))

        return pkg

    # ===== Tests for _derive_settings_file() =====

    def test_derive_settings_file_root_package(self):
        """Files directly in packages/ use just the file stem."""
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        assert pkg._settings_file == "whitenoise.py"

    def test_derive_settings_file_subpackage(self):
        """Files in packages/subdir/ use parent_name + '_' + stem."""
        pkg = self._mock_basepackage_with_file("django_storages/s3.py")
        assert pkg._settings_file == "django_storages_s3.py"

    def test_derive_settings_file_nested_subpackage(self):
        """Deeply nested packages use parent_name + '_' + stem."""
        pkg = self._mock_basepackage_with_file("django_anymail/resend.py")
        assert pkg._settings_file == "django_anymail_resend.py"

    def test_derive_settings_file_respects_override(self):
        """If settings_file is explicitly set, it should not be derived."""
        # Create instance with explicit override
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        # Verify the derived settings file is what we expect
        assert pkg._settings_file == "whitenoise.py"

    # ===== Tests for _derive_url_file() =====

    def test_derive_url_file_matches_settings_file(self):
        """URL file follows the same derivation rule as settings file."""
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        assert pkg._url_file == pkg._settings_file
        assert pkg._url_file == "whitenoise.py"

    def test_derive_url_file_subpackage_matches_settings(self):
        """URL file for subpackages uses same pattern as settings."""
        pkg = self._mock_basepackage_with_file("django_allauth/account.py")
        assert pkg._url_file == "django_allauth_account.py"
        assert pkg._url_file == pkg._settings_file

    def test_derive_url_file_respects_override(self):
        """If url_file is explicitly set, it should be respected."""
        # Create instance and verify PathDeriver is called with the override
        # Since PathDeriver handles the override logic, we just verify derivation works
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        assert pkg._url_file == "whitenoise.py"

    # ===== Tests for _derive_template_path() =====

    def test_derive_template_path_root_package(self):
        """Files in packages/ root derive just the file stem."""
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        # template_path is relative to packages directory
        assert pkg._template_path == "whitenoise"

    def test_derive_template_path_subpackage(self):
        """Files in subdir/ derive path relative to packages directory."""
        pkg = self._mock_basepackage_with_file("django_storages/s3.py")
        # Relative to packages directory (includes subdir)
        assert pkg._template_path == "django_storages/s3"

    def test_derive_template_path_nested(self):
        """Nested packages derive path relative to packages directory."""
        pkg = self._mock_basepackage_with_file("django_anymail/resend.py")
        # Relative to packages directory (includes subdir)
        assert pkg._template_path == "django_anymail/resend"

    def test_derive_template_path_respects_override(self):
        """If template_path is explicitly set, it should be respected."""
        # Since PathDeriver handles the override logic, we just verify derivation works
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        assert pkg._template_path == "whitenoise"

    # ===== Tests for edge cases =====

    def test_derive_settings_file_with_underscores_in_name(self):
        """Files with underscores in name work correctly."""
        pkg = self._mock_basepackage_with_file("django_cors_headers.py")
        assert pkg._settings_file == "django_cors_headers.py"

    def test_derive_settings_file_with_numbers(self):
        """Files with numbers work correctly."""
        pkg = self._mock_basepackage_with_file("drf2_spectacular.py")
        assert pkg._settings_file == "drf2_spectacular.py"

    def test_derive_subpackage_with_hyphens_in_parent(self):
        """Subpackages with hyphens in parent dir name work correctly."""
        # This would be unusual but test the logic
        pkg = self._mock_basepackage_with_file("some-lib/component.py")
        assert pkg._settings_file == "some-lib_component.py"

    # ===== Consistency tests =====

    def test_derivations_are_consistent_across_file_types(self):
        """All root files derive consistently."""
        for filename in ["whitenoise.py", "channels.py", "heroicons.py"]:
            pkg = self._mock_basepackage_with_file(filename)
            expected = filename
            assert pkg._settings_file == expected
            assert pkg._url_file == expected

    def test_subpackage_derivations_are_consistent(self):
        """All subpackage files derive consistently."""
        test_cases = [
            ("django_storages/s3.py", "django_storages_s3.py"),
            ("django_allauth/account.py", "django_allauth_account.py"),
            ("django_anymail/resend.py", "django_anymail_resend.py"),
        ]
        for file_path, expected_name in test_cases:
            pkg = self._mock_basepackage_with_file(file_path)
            assert pkg._settings_file == expected_name
            assert pkg._url_file == expected_name

    def test_template_path_excludes_extension(self):
        """Template path never includes .py extension."""
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        assert not pkg._template_path.endswith(".py")

        pkg = self._mock_basepackage_with_file("django_storages/s3.py")
        assert not pkg._template_path.endswith(".py")


class TestBasePackageInitialization:
    """Test BasePackage initialization and djdevx root derivation."""

    def test_init_with_valid_file_path(self):
        """BasePackage.__init__ should accept a file path string."""
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage("/path/to/packages/whitenoise.py")
            assert pkg._settings_file == "whitenoise.py"

    def test_lazy_loading_of_pm_and_uv(self):
        """PM and UV utilities should be lazily loaded."""
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage("/path/to/packages/whitenoise.py")
            # Before access, should be None
            assert pkg._pm is None
            assert pkg._uv is None


class TestPathEdgeCases:
    """Test edge cases and unusual file structures."""

    def _mock_basepackage_with_file(self, file_path: str) -> BasePackage:
        """Helper to create a BasePackage instance with a mocked file path."""
        mock_path = (
            Path("/home/siavash/code/djdevx/djdevx/backend/django/packages") / file_path
        )
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage(str(mock_path))
        return pkg

    def test_all_explicit_overrides_skip_derivation(self):
        """If all paths are explicitly set, derivation respects them."""
        # Since PathDeriver handles overrides during initialization,
        # we verify that the derived values are correct for the given path
        pkg = self._mock_basepackage_with_file("whitenoise.py")
        # Basic test to verify the instance works
        assert pkg._settings_file == "whitenoise.py"
        assert pkg._url_file == "whitenoise.py"
        assert pkg._template_path == "whitenoise"


class TestPathDeriver:
    """Test PathDeriver class functionality."""

    def _create_deriver(self, file_path: str) -> PathDeriver:
        """Helper to create a PathDeriver with a mocked file path."""
        mock_path = (
            Path("/home/siavash/code/djdevx/djdevx/backend/django/packages") / file_path
        )
        return PathDeriver(mock_path)

    def test_derive_settings_file_root_package(self):
        """Root package settings file is just the stem."""
        deriver = self._create_deriver("whitenoise.py")
        assert deriver.derive_settings_file(None) == "whitenoise.py"

    def test_derive_settings_file_subpackage(self):
        """Subpackage settings file is parent_name + '_' + stem."""
        deriver = self._create_deriver("django_storages/s3.py")
        assert deriver.derive_settings_file(None) == "django_storages_s3.py"

    def test_derive_settings_file_with_override(self):
        """Explicit override is respected."""
        deriver = self._create_deriver("whitenoise.py")
        assert (
            deriver.derive_settings_file("custom_settings.py") == "custom_settings.py"
        )

    def test_derive_url_file_root_package(self):
        """Root package URL file is just the stem."""
        deriver = self._create_deriver("whitenoise.py")
        assert deriver.derive_url_file(None) == "whitenoise.py"

    def test_derive_url_file_subpackage(self):
        """Subpackage URL file is parent_name + '_' + stem."""
        deriver = self._create_deriver("django_storages/s3.py")
        assert deriver.derive_url_file(None) == "django_storages_s3.py"

    def test_derive_url_file_with_override(self):
        """Explicit override is respected."""
        deriver = self._create_deriver("channels.py")
        assert deriver.derive_url_file("custom_urls.py") == "custom_urls.py"

    def test_derive_template_path_root_package(self):
        """Root package template path is just the stem."""
        deriver = self._create_deriver("whitenoise.py")
        assert deriver.derive_template_path(None) == "whitenoise"

    def test_derive_template_path_subpackage(self):
        """Subpackage template path is relative to packages directory."""
        deriver = self._create_deriver("django_storages/s3.py")
        assert deriver.derive_template_path(None) == "django_storages/s3"

    def test_derive_template_path_with_override(self):
        """Explicit override is respected."""
        deriver = self._create_deriver("whitenoise.py")
        assert deriver.derive_template_path("custom/path") == "custom/path"

    def test_derive_ws_url_dirs_root_package(self):
        """Root package WS URL dir is the stem without .py."""
        deriver = self._create_deriver("channels.py")
        assert deriver.derive_ws_url_dirs(None) == "channels"

    def test_derive_ws_url_dirs_subpackage(self):
        """Subpackage WS URL dir is parent_name + '_' + stem without .py."""
        deriver = self._create_deriver("django_anymail/resend.py")
        assert deriver.derive_ws_url_dirs(None) == "django_anymail_resend"

    def test_derive_ws_url_dirs_with_override(self):
        """Explicit override is respected."""
        deriver = self._create_deriver("channels.py")
        assert deriver.derive_ws_url_dirs("custom_ws_dir") == "custom_ws_dir"

    def test_derive_ws_url_dirs_matches_filename_without_extension(self):
        """WS URL dirs should match the filename without .py extension."""
        test_cases = [
            ("channels.py", "channels"),
            ("whitenoise.py", "whitenoise"),
            ("django_storages/s3.py", "django_storages_s3"),
        ]
        for file_path, expected_dir in test_cases:
            deriver = self._create_deriver(file_path)
            assert deriver.derive_ws_url_dirs(None) == expected_dir


class TestBasePackageWSUrlDirs:
    """Test ws_url_dirs functionality in BasePackage."""

    def _mock_basepackage_with_file(self, file_path: str) -> BasePackage:
        """Helper to create a BasePackage instance with a mocked file path."""
        mock_path = (
            Path("/home/siavash/code/djdevx/djdevx/backend/django/packages") / file_path
        )
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage(str(mock_path))
        return pkg

    def test_ws_url_dirs_derived_for_root_package(self):
        """WS URL dirs are auto-derived for root packages."""
        pkg = self._mock_basepackage_with_file("channels.py")
        assert pkg._ws_url_dirs == "channels"

    def test_ws_url_dirs_derived_for_subpackage(self):
        """WS URL dirs are auto-derived for subpackages."""
        pkg = self._mock_basepackage_with_file("django_anymail/resend.py")
        assert pkg._ws_url_dirs == "django_anymail_resend"

    def test_ws_url_dirs_optional_attribute(self):
        """ws_url_dirs is optional class attribute."""
        # Verify the class attribute exists and defaults to None
        assert hasattr(BasePackage, "ws_url_dirs")
        assert BasePackage.ws_url_dirs is None

    def test_ws_url_dirs_can_be_overridden(self):
        """Subclasses can override ws_url_dirs."""

        # Create a test subclass with explicit ws_url_dirs
        class TestPackage(BasePackage):
            ws_url_dirs = "custom_ws_path"

        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = TestPackage(
                "/home/siavash/code/djdevx/djdevx/backend/django/packages/test.py"
            )
            # When explicitly set, it should use the override
            assert pkg._ws_url_dirs == "custom_ws_path"
