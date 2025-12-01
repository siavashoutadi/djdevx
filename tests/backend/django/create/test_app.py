from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "app"


def test_create_app(temp_dir):
    """
    Test create app functionality.
    """
    result = runner.invoke(
        app,
        [
            "new",
            "backend",
            "django",
            "--project-name",
            "my_django_project",
            "--project-description",
            "A sample Django backend project",
            "--project-directory",
            str(temp_dir),
            "--python-version",
            "3.14",
            "--backend-root",
            "backend",
        ],
    )

    assert result.exit_code == 0

    APPLICATION_NAME = "home"
    cwd = Path.cwd()
    try:
        os.chdir(temp_dir)

        result = runner.invoke(
            app,
            [
                "backend",
                "django",
                "create",
                "app",
                "--application-name",
                APPLICATION_NAME,
            ],
        )
    finally:
        os.chdir(cwd)

    assert result.exit_code == 0

    home_files = [
        f.relative_to(DATA_DIR) for f in DATA_DIR.rglob("home/*") if f.is_file()
    ]

    for relative_path in home_files:
        created_file = temp_dir / "backend" / relative_path

        assert created_file.exists(), f"Missing file: {relative_path}"
        expected_content = (DATA_DIR / relative_path).read_text()
        actual_content = created_file.read_text()

        assert actual_content == expected_content, (
            f"Content mismatch in file: {relative_path}"
        )

    additional_files = [
        f.relative_to(DATA_DIR)
        for f in DATA_DIR.rglob("*")
        if f.is_file() and not str(f.relative_to(DATA_DIR)).startswith("home/")
    ]

    for relative_path in additional_files:
        created_file = temp_dir / "backend" / relative_path

        assert created_file.exists(), f"Missing file: {relative_path}"
        expected_content = (DATA_DIR / relative_path).read_text()
        actual_content = created_file.read_text()

        assert actual_content == expected_content, (
            f"Content mismatch in file: {relative_path}"
        )
