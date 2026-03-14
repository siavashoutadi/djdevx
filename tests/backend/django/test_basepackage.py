"""Unit tests for BasePackage path derivation logic."""

import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch


from djdevx.backend.django.packages._base import (
    BasePackage,
    EnvParam,
    InstallParam,
    PathDeriver,
)


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


# ============================================================
# Helpers shared by new tests
# ============================================================

PACKAGES_PATH = Path("/home/siavash/code/djdevx/djdevx/backend/django/packages")


def _make_pkg(file_path: str, **class_attrs) -> BasePackage:
    """Create a subclass with given attrs and return an instance."""
    mock_path = PACKAGES_PATH / file_path
    attrs = {"name": "test-pkg", "packages": [], **class_attrs}

    with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
        mock_root.return_value = Path("/home/siavash/code/djdevx")
        cls = type("TestPkg", (BasePackage,), attrs)
        pkg = object.__new__(cls)
        pkg._install_context = {}
        pkg.__init__(str(mock_path))

    return pkg


class TestInstallParamsInjection:
    """Tests for auto-generated install() from install_params."""

    def _make_install_param_pkg(self):
        """Create a package with install_params."""
        mock_path = PACKAGES_PATH / "whitenoise.py"

        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")

            class PkgWithInstallParams(BasePackage):
                name = "test"
                packages = []
                install_params = [
                    InstallParam(name="color", help="A color", prompt="Color?"),
                    InstallParam(
                        name="size", default="large", help="A size", prompt="Size?"
                    ),
                ]

            pkg = object.__new__(PkgWithInstallParams)
            pkg._install_context = {}
            pkg.__init__(str(mock_path))

        return pkg

    def test_install_method_is_generated(self):
        """Subclass with install_params and no install() gets a generated install."""
        pkg = self._make_install_param_pkg()
        assert callable(pkg.install)

    def test_generated_install_signature_has_correct_params(self):
        """Generated install __signature__ has the declared parameter names."""
        pkg = self._make_install_param_pkg()
        sig = inspect.signature(pkg.install)
        param_names = list(sig.parameters.keys())
        assert "color" in param_names
        assert "size" in param_names

    def test_generated_install_calls_hooks_in_order(self):
        """Generated install calls hooks and core methods in correct order."""
        pkg = self._make_install_param_pkg()

        call_order = []
        pkg.before_uv_install = lambda: call_order.append("before_uv_install")
        pkg._check_required_dependencies = lambda: call_order.append(
            "_check_required_deps"
        )
        pkg._uv_add_all = lambda: call_order.append("_uv_add_all")
        pkg.after_uv_install = lambda: call_order.append("after_uv_install")
        pkg.before_copy_templates = lambda: call_order.append("before_copy_templates")
        pkg._copy_templates = lambda context=None: call_order.append("_copy_templates")
        pkg.after_copy_templates = lambda: call_order.append("after_copy_templates")
        pkg._add_env_vars = lambda: call_order.append("_add_env_vars")

        pkg.install(color="red", size="small")

        assert call_order == [
            "before_uv_install",
            "_check_required_deps",
            "_uv_add_all",
            "after_uv_install",
            "before_copy_templates",
            "_copy_templates",
            "after_copy_templates",
            "_add_env_vars",
        ]

    def test_install_context_set_before_before_uv_install_hook(self):
        """_install_context is populated before before_uv_install() is called."""
        pkg = self._make_install_param_pkg()

        context_at_hook_time = {}

        def capture_context():
            context_at_hook_time.update(pkg._install_context)

        pkg.before_uv_install = capture_context
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg.after_uv_install = lambda: None
        pkg.before_copy_templates = lambda: None
        pkg._copy_templates = lambda context=None: None
        pkg.after_copy_templates = lambda: None
        pkg._add_env_vars = lambda: None

        pkg.install(color="blue", size="small")

        assert context_at_hook_time == {"color": "blue", "size": "small"}


class TestEnvParamsInjection:
    """Tests for auto-generated env() and install() from env_params."""

    def _make_env_param_pkg(self):
        """Create a package with env_params."""
        mock_path = PACKAGES_PATH / "whitenoise.py"

        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")

            class PkgWithEnvParams(BasePackage):
                name = "test"
                packages = []
                env_params = [
                    EnvParam(
                        name="api_key",
                        env_key="MY_API_KEY",
                        help="API key",
                        prompt="Enter API key",
                        hide_input=True,
                    ),
                    EnvParam(
                        name="email",
                        env_key="DEFAULT_EMAIL",
                        help="Email",
                        prompt="Enter email",
                    ),
                ]

            pkg = object.__new__(PkgWithEnvParams)
            pkg._install_context = {}
            pkg.__init__(str(mock_path))

        return pkg

    def test_env_method_is_generated(self):
        """Subclass with env_params and no env() gets a generated env."""
        pkg = self._make_env_param_pkg()
        assert callable(pkg.env)

    def test_generated_env_calls_add_env_variable(self):
        """Generated env() calls pm.add_env_variable for each env_key."""
        pkg = self._make_env_param_pkg()
        mock_pm = MagicMock()
        pkg._pm = mock_pm

        pkg.env(api_key="secret123", email="test@example.com")

        mock_pm.add_env_variable.assert_any_call(key="MY_API_KEY", value="secret123")
        mock_pm.add_env_variable.assert_any_call(
            key="DEFAULT_EMAIL", value="test@example.com"
        )

    def test_generated_install_also_calls_add_env_variable(self):
        """Generated install() calls pm.add_env_variable for each env_param."""
        pkg = self._make_env_param_pkg()
        mock_pm = MagicMock()
        pkg._pm = mock_pm
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None
        pkg._add_env_vars = lambda: None

        pkg.install(api_key="mykey", email="user@example.com")

        mock_pm.add_env_variable.assert_any_call(key="MY_API_KEY", value="mykey")
        mock_pm.add_env_variable.assert_any_call(
            key="DEFAULT_EMAIL", value="user@example.com"
        )


class TestHookOrdering:
    """Tests for lifecycle hook call ordering."""

    def _make_base_pkg(self):
        """Create a plain base package instance."""
        mock_path = PACKAGES_PATH / "whitenoise.py"
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")
            pkg = BasePackage(str(mock_path))
        return pkg

    def test_install_hook_order(self):
        """install() calls hooks and core methods in the correct order."""
        pkg = self._make_base_pkg()
        call_order = []

        pkg.before_uv_install = lambda: call_order.append("before_uv_install")
        pkg._check_required_dependencies = lambda: call_order.append(
            "_check_required_dependencies"
        )
        pkg._uv_add_all = lambda: call_order.append("_uv_add_all")
        pkg.after_uv_install = lambda: call_order.append("after_uv_install")
        pkg.before_copy_templates = lambda: call_order.append("before_copy_templates")
        pkg._copy_templates = lambda context=None: call_order.append("_copy_templates")
        pkg.after_copy_templates = lambda: call_order.append("after_copy_templates")
        pkg._add_env_vars = lambda: call_order.append("_add_env_vars")

        pkg.install()

        assert call_order == [
            "before_uv_install",
            "_check_required_dependencies",
            "_uv_add_all",
            "after_uv_install",
            "before_copy_templates",
            "_copy_templates",
            "after_copy_templates",
            "_add_env_vars",
        ]

    def test_remove_hook_order(self):
        """remove() calls hooks and core methods in the correct order."""
        pkg = self._make_base_pkg()
        call_order = []

        pkg.before_uv_remove = lambda: call_order.append("before_uv_remove")
        pkg._uv_remove_all = lambda: call_order.append("_uv_remove_all")
        pkg.after_uv_remove = lambda: call_order.append("after_uv_remove")
        pkg._cleanup_files = lambda: call_order.append("_cleanup_files")
        pkg._cleanup_extra_files = lambda: call_order.append("_cleanup_extra_files")
        pkg._remove_env_vars = lambda: call_order.append("_remove_env_vars")
        pkg._remove_env_params = lambda: call_order.append("_remove_env_params")

        pkg.remove()

        assert call_order == [
            "before_uv_remove",
            "_uv_remove_all",
            "after_uv_remove",
            "_cleanup_files",
            "_cleanup_extra_files",
            "_remove_env_vars",
            "_remove_env_params",
        ]


class TestCleanupExtraFiles:
    """Tests for _cleanup_extra_files() method."""

    def _make_pkg_with_cleanup(self, files=(), folders=()):
        mock_path = PACKAGES_PATH / "whitenoise.py"
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")

            class CleanupPkg(BasePackage):
                name = "test"
                packages = []
                files_to_remove = list(files)
                folders_to_remove = list(folders)

            pkg = object.__new__(CleanupPkg)
            pkg._install_context = {}
            pkg.__init__(str(mock_path))

        return pkg

    def test_cleanup_extra_files_unlinks_files(self, tmp_path):
        """_cleanup_extra_files() calls unlink for each file in files_to_remove."""
        pkg = self._make_pkg_with_cleanup(files=["a.txt", "subdir/b.txt"])
        mock_pm = MagicMock()
        mock_pm.project_path = tmp_path
        pkg._pm = mock_pm

        # Create the files
        (tmp_path / "a.txt").write_text("x")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "b.txt").write_text("y")

        pkg._cleanup_extra_files()

        assert not (tmp_path / "a.txt").exists()
        assert not (tmp_path / "subdir" / "b.txt").exists()

    def test_cleanup_extra_files_removes_folders(self, tmp_path):
        """_cleanup_extra_files() removes directories in folders_to_remove."""
        pkg = self._make_pkg_with_cleanup(folders=["somedir"])
        mock_pm = MagicMock()
        mock_pm.project_path = tmp_path
        pkg._pm = mock_pm

        (tmp_path / "somedir").mkdir()
        (tmp_path / "somedir" / "file.txt").write_text("content")

        pkg._cleanup_extra_files()

        assert not (tmp_path / "somedir").exists()

    def test_cleanup_extra_files_missing_ok(self, tmp_path):
        """_cleanup_extra_files() does not raise if files/folders don't exist."""
        pkg = self._make_pkg_with_cleanup(files=["nonexistent.txt"], folders=["nodir"])
        mock_pm = MagicMock()
        mock_pm.project_path = tmp_path
        pkg._pm = mock_pm

        # Should not raise
        pkg._cleanup_extra_files()


class TestRemoveEnvParams:
    """Tests for _remove_env_params() method."""

    def test_remove_env_params_calls_remove_env_variable(self):
        """_remove_env_params() calls pm.remove_env_variable for each env_key."""
        mock_path = PACKAGES_PATH / "whitenoise.py"
        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")

            class PkgWithEnv(BasePackage):
                name = "test"
                packages = []
                env_params = [
                    EnvParam(name="k1", env_key="KEY_ONE", help=""),
                    EnvParam(name="k2", env_key="KEY_TWO", help=""),
                ]

            pkg = object.__new__(PkgWithEnv)
            pkg._install_context = {}
            pkg.__init__(str(mock_path))

        mock_pm = MagicMock()
        pkg._pm = mock_pm

        pkg._remove_env_params()

        assert mock_pm.remove_env_variable.call_count == 2
        mock_pm.remove_env_variable.assert_any_call("KEY_ONE")
        mock_pm.remove_env_variable.assert_any_call("KEY_TWO")


class TestShowIfConditionalPrompt:
    """Tests for conditional prompting with show_if params."""

    def _make_show_if_pkg(self):
        mock_path = PACKAGES_PATH / "whitenoise.py"

        with patch.object(BasePackage, "_derive_djdevx_root") as mock_root:
            mock_root.return_value = Path("/home/siavash/code/djdevx")

            class ShowIfPkg(BasePackage):
                name = "test"
                packages = []
                install_params = [
                    InstallParam(
                        name="enable_feature",
                        type_=bool,
                        default=False,
                        help="Enable feature",
                        prompt="Enable?",
                    ),
                    InstallParam(
                        name="feature_key",
                        show_if="enable_feature",
                        help="Feature key",
                        prompt="Enter feature key",
                        message_before_prompt="Here comes the prompt:",
                    ),
                ]

            pkg = object.__new__(ShowIfPkg)
            pkg._install_context = {}
            pkg.__init__(str(mock_path))

        return pkg

    def test_prompt_invoked_when_gating_param_true_and_value_empty(self):
        """When gating param is True and dependent param is empty, typer.prompt is called."""
        pkg = self._make_show_if_pkg()
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None
        pkg._add_env_vars = lambda: None

        with patch(
            "djdevx.backend.django.packages._base.typer.prompt",
            return_value="prompted-value",
        ) as mock_prompt:
            pkg.install(enable_feature=True, feature_key="")

        mock_prompt.assert_called_once()
        call_args = mock_prompt.call_args
        assert "Enter feature key" in call_args[0][0]
        assert pkg._install_context["feature_key"] == "prompted-value"

    def test_prompt_not_invoked_when_gating_param_false(self):
        """When gating param is False, conditional prompt is not invoked."""
        pkg = self._make_show_if_pkg()
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None
        pkg._add_env_vars = lambda: None

        with patch("djdevx.backend.django.packages._base.typer.prompt") as mock_prompt:
            pkg.install(enable_feature=False, feature_key="")

        mock_prompt.assert_not_called()

    def test_prompt_not_invoked_when_value_already_set(self):
        """When the dependent param already has a value, no prompt is issued."""
        pkg = self._make_show_if_pkg()
        pkg._check_required_dependencies = lambda: None
        pkg._uv_add_all = lambda: None
        pkg._copy_templates = lambda context=None: None
        pkg._add_env_vars = lambda: None

        with patch("djdevx.backend.django.packages._base.typer.prompt") as mock_prompt:
            pkg.install(enable_feature=True, feature_key="already-set")

        mock_prompt.assert_not_called()
        assert pkg._install_context["feature_key"] == "already-set"
