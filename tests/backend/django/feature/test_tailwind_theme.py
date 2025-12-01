import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_tailwind_theme_install_and_remove(temp_dir):
    """
    Test Tailwind theme installation and removal in one workflow.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

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

    assert result.exit_code == 0, f"Install failed: {result.output}"

    theme_css_file = backend_dir / "tailwind" / "src" / "css" / "theme.css"
    input_css_file = backend_dir / "tailwind" / "src" / "css" / "input.css"

    assert theme_css_file.exists(), "theme.css file should be created"

    theme_content = theme_css_file.read_text()
    assert "--color-primary-50:" in theme_content, (
        "Primary color palette should be generated"
    )

    input_content = input_css_file.read_text()
    assert '@import "./theme.css";' in input_content, (
        "Theme import should be added to input.css"
    )

    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-theme", "remove"]
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not theme_css_file.exists(), "theme.css file should be removed"

    input_content = input_css_file.read_text()
    assert '@import "./theme.css";' not in input_content, (
        "Theme import should be removed from input.css"
    )


def test_tailwind_theme_invalid_hex_color(temp_dir):
    """
    Test that invalid hex colors are rejected.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

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
            "#INVALIDHEX",
        ],
    )

    assert result.exit_code != 0, "Invalid hex color should be rejected"
    assert "Invalid hex color format" in result.output


def test_tailwind_theme_invalid_css_variable(temp_dir):
    """
    Test that invalid CSS variables are rejected.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

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
            "--invalid-var-name!",
        ],
    )

    assert result.exit_code != 0, "Invalid CSS variable should be rejected"
    assert "Invalid color format" in result.output


def test_tailwind_theme_install_idempotent(temp_dir):
    """
    Test that installing theme multiple times is idempotent.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["backend", "django", "packages", "django-tailwind-cli", "install"]
    )
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    for _ in range(2):
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
        assert result.exit_code == 0, (
            f"Install should work on iteration: {result.output}"
        )

    input_css_file = backend_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    import_count = input_content.count('@import "./theme.css";')
    assert import_count == 1, (
        f"Theme import should appear exactly once, found {import_count} times"
    )


def test_tailwind_theme_remove_when_not_installed(temp_dir):
    """
    Test that removing theme when not installed doesn't cause errors.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["backend", "django", "feature", "tailwind-theme", "remove"]
    )

    assert result.exit_code == 0, (
        f"Remove should succeed even when not installed: {result.output}"
    )
