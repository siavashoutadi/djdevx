from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-snakeoil"


def test_django_snakeoil_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django_snakeoil",
        ],
    )
    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_snakeoil.py"
    assert settings_file.exists(), "Settings file not created"

    expected_content = (
        DATA_DIR / "settings" / "packages" / "django_snakeoil.py"
    ).read_text()
    assert settings_file.read_text() == expected_content

    assert PixiRunner().has_dependency("django-snakeoil")

    base_template_path = temp_dir / "templates" / "_base.html"
    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "snakeoil" in base_content
        assert "{% meta %}" in base_content

    result = runner.invoke(app, ["packages", "remove", "django_snakeoil"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not PixiRunner().has_dependency("django-snakeoil")

    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "{% load snakeoil %}" not in base_content
        assert "{% meta %}" not in base_content
