"""
Shared test utilities for djdevx tests.
"""

from pathlib import Path
from typer.testing import CliRunner
from djdevx.main import app


def create_test_django_backend(temp_dir: Path, runner: CliRunner) -> Path:
    """
    Create a test Django backend project in the given temporary directory.

    Args:
        temp_dir: The temporary directory to create the project in
        runner: The CliRunner instance to use for invoking commands

    Returns:
        Path: The backend directory path

    Raises:
        AssertionError: If the project creation fails
    """
    result = runner.invoke(
        app,
        [
            "new",
            "backend",
            "django",
            "--project-name",
            "test_django_project",
            "--project-description",
            "A test Django backend project",
            "--project-directory",
            str(temp_dir),
            "--python-version",
            "3.14",
            "--backend-root",
            "backend",
        ],
    )

    assert result.exit_code == 0, f"Django backend creation failed: {result.output}"

    backend_dir = temp_dir / "backend"
    assert backend_dir.exists(), "Backend directory was not created"

    return backend_dir
