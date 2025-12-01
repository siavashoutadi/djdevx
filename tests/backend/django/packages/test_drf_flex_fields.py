from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "drf-flex-fields"


def test_drf_flex_fields_install_and_remove(temp_dir):
    """
    Test drf-flex-fields package installation and removal.
    """

    create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-flex-fields",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    assert DjangoProjectManager().has_dependency("drf-flex-fields"), (
        "drf-flex-fields dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-flex-fields",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not DjangoProjectManager().has_dependency("drf-flex-fields"), (
        "drf-flex-fields dependency found after removal"
    )
