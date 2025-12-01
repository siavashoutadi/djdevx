import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_drf_nested_routers_install_and_remove(temp_dir):
    """
    Test drf-nested-routers package installation and removal.
    """

    create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-nested-routers",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # This package doesn't create any files, just installs the dependency
    assert DjangoProjectManager().has_dependency("drf-nested-routers"), (
        "drf-nested-routers dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-nested-routers",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not DjangoProjectManager().has_dependency("drf-nested-routers"), (
        "drf-nested-routers dependency found after removal"
    )
