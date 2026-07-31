"""
Shared test utilities for djdevx tests.
"""

from pathlib import Path
from typer.testing import CliRunner
from djdevx.main import app


def create_test_django_project(temp_dir: Path, runner: CliRunner) -> Path:
    """
    Create a test Django project in the given temporary directory.

    Args:
        temp_dir: The temporary directory to create the project in
        runner: The CliRunner instance to use for invoking commands

    Returns:
        Path: The project root directory path (same as temp_dir)

    Raises:
        AssertionError: If the project creation fails
    """
    result = runner.invoke(
        app,
        [
            "new",
            "--project-name",
            "test_django_project",
            "--project-description",
            "A test Django backend project",
            "--project-directory",
            str(temp_dir),
            "--python-version",
            "3.14",
            "--no-git-init",
        ],
    )

    assert result.exit_code == 0, f"Django project creation failed: {result.output}"

    return temp_dir
