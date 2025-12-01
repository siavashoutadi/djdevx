import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_tailwind_ui_install_and_remove(temp_dir):
    """
    Test Tailwind UI installation and removal.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install heroicons dependency first
    result = runner.invoke(
        app, ["backend", "django", "packages", "heroicons", "install"]
    )
    assert result.exit_code == 0, f"Heroicons install failed: {result.output}"

    # Install django-tailwind-cli dependency
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-tailwind-cli", "install"]
    )
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    # Install tailwind theme dependency
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "tailwind-theme",
            "install",
            "--primary-color",
            "#3B82F6",
            "--secondary-color",
            "#64748B",
            "--accent-color",
            "#F97316",
            "--neutral-color",
            "#71717A",
            "--bg-light",
            "#FFFFFF",
            "--bg-secondary-light",
            "#F1F5F9",
            "--bg-tertiary-light",
            "#E2E8F0",
            "--text-light",
            "#0F172A",
            "--text-secondary-light",
            "#334155",
            "--text-muted-light",
            "#64748B",
            "--bg-dark",
            "#0F172A",
            "--bg-secondary-dark",
            "#1E293B",
            "--bg-tertiary-dark",
            "#334155",
            "--text-dark",
            "#F1F5F9",
            "--text-secondary-dark",
            "#CBD5E1",
            "--text-muted-dark",
            "#64748B",
        ],
    )
    assert result.exit_code == 0, f"Tailwind theme install failed: {result.output}"

    # Now install Tailwind UI
    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-ui", "install"]
    )
    assert result.exit_code == 0, f"Tailwind UI install failed: {result.output}"

    # Verify tailwind_ui app directory created
    tailwind_ui_app_dir = backend_dir / "tailwind_ui"
    assert tailwind_ui_app_dir.exists(), "tailwind_ui app directory not created"

    # Verify app files exist
    apps_file = tailwind_ui_app_dir / "apps.py"
    assert apps_file.exists(), "tailwind_ui apps.py not created"

    views_file = tailwind_ui_app_dir / "views.py"
    assert views_file.exists(), "tailwind_ui views.py not created"

    urls_file = tailwind_ui_app_dir / "urls.py"
    assert urls_file.exists(), "tailwind_ui urls.py not created"

    # Verify CSS directory and files created
    tailwind_ui_css_dir = backend_dir / "tailwind" / "src" / "css" / "tailwind-ui"
    assert tailwind_ui_css_dir.exists(), "tailwind-ui CSS directory not created"

    all_css_file = tailwind_ui_css_dir / "all.css"
    assert all_css_file.exists(), "tailwind-ui all.css not created"

    # Verify settings and URL configuration files created
    settings_file = backend_dir / "settings" / "apps" / "tailwind_ui.py"
    assert settings_file.exists(), "tailwind_ui settings file not created"

    urls_config_file = backend_dir / "urls" / "apps" / "tailwind_ui.py"
    assert urls_config_file.exists(), "tailwind_ui URLs config file not created"

    # Verify input.css has been modified to include UI import
    input_css_file = backend_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    assert '@import "./tailwind-ui/all.css";' in input_content, (
        "tailwind-ui import not added to input.css"
    )

    # Test removal
    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-ui", "remove"]
    )
    assert result.exit_code == 0, f"Tailwind UI remove failed: {result.output}"

    # Verify app directory removed
    assert not tailwind_ui_app_dir.exists(), "tailwind_ui app directory not removed"

    # Verify CSS directory removed
    assert not tailwind_ui_css_dir.exists(), "tailwind-ui CSS directory not removed"

    # Verify settings and URL files removed
    assert not settings_file.exists(), "tailwind_ui settings file not removed"
    assert not urls_config_file.exists(), "tailwind_ui URLs config file not removed"

    # Verify input.css import removed
    input_content_after = input_css_file.read_text()
    assert '@import "./tailwind-ui/all.css";' not in input_content_after, (
        "tailwind-ui import not removed from input.css"
    )


def test_tailwind_ui_missing_heroicons_dependency(temp_dir):
    """
    Test that Tailwind UI installation fails when heroicons is not installed.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install django-tailwind-cli but not heroicons
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-tailwind-cli", "install"]
    )
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    # Try to install Tailwind UI without heroicons
    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-ui", "install"]
    )

    assert result.exit_code != 0, "Tailwind UI install should fail without heroicons"
    assert "Heroicons is not installed" in result.output


def test_tailwind_ui_missing_theme_dependency(temp_dir):
    """
    Test that Tailwind UI installation fails when theme is not installed.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install heroicons and django-tailwind-cli but not theme
    result = runner.invoke(
        app, ["backend", "django", "packages", "heroicons", "install"]
    )
    assert result.exit_code == 0, f"Heroicons install failed: {result.output}"

    result = runner.invoke(
        app, ["backend", "django", "packages", "django-tailwind-cli", "install"]
    )
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    # Try to install Tailwind UI without theme
    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-ui", "install"]
    )

    assert result.exit_code != 0, "Tailwind UI install should fail without theme"
    assert "Tailwind theme is not installed" in result.output


def test_tailwind_ui_install_idempotent(temp_dir):
    """
    Test that installing Tailwind UI multiple times is idempotent.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install dependencies
    result = runner.invoke(
        app, ["backend", "django", "packages", "heroicons", "install"]
    )
    assert result.exit_code == 0, f"Heroicons install failed: {result.output}"

    result = runner.invoke(
        app, ["backend", "django", "packages", "django-tailwind-cli", "install"]
    )
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "tailwind-theme",
            "install",
            "--primary-color",
            "#3B82F6",
            "--secondary-color",
            "#64748B",
            "--accent-color",
            "#F97316",
            "--neutral-color",
            "#71717A",
            "--bg-light",
            "#FFFFFF",
            "--bg-secondary-light",
            "#F1F5F9",
            "--bg-tertiary-light",
            "#E2E8F0",
            "--text-light",
            "#0F172A",
            "--text-secondary-light",
            "#334155",
            "--text-muted-light",
            "#64748B",
            "--bg-dark",
            "#0F172A",
            "--bg-secondary-dark",
            "#1E293B",
            "--bg-tertiary-dark",
            "#334155",
            "--text-dark",
            "#F1F5F9",
            "--text-secondary-dark",
            "#CBD5E1",
            "--text-muted-dark",
            "#64748B",
        ],
    )
    assert result.exit_code == 0, f"Tailwind theme install failed: {result.output}"

    # Install Tailwind UI multiple times
    for _ in range(2):
        result = runner.invoke(
            app, ["backend", "django", "feature", "tailwind-ui", "install"]
        )
        assert result.exit_code == 0, f"Tailwind UI install failed: {result.output}"

    # Verify only one import exists in input.css
    input_css_file = backend_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    import_count = input_content.count('@import "./tailwind-ui/all.css";')
    assert import_count == 1, f"Expected 1 tailwind-ui import, found {import_count}"


def test_tailwind_ui_remove_when_not_installed(temp_dir):
    """
    Test that removing Tailwind UI when not installed doesn't cause errors.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-ui", "remove"]
    )

    assert result.exit_code == 0, (
        f"Remove should succeed even when not installed: {result.output}"
    )
