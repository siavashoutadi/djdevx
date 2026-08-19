"""Format output files using prek pre-commit hooks via pixi."""

from pathlib import Path

from ..project.pixi_runner import PixiRunner
from ..console.print import print_console


def format_files(files: list[Path], project_root: Path) -> None:
    """Run prek pre-commit hooks on the given files via pixi.

    Args:
        files: List of absolute file paths to format.
        project_root: Project root directory (where pixi.toml / prek.toml live).
    """
    if not files:
        return
    runner = PixiRunner(project_root=project_root)
    str_files = [str(f) for f in files]
    print_console.step("Formatting files ...")
    result = runner.run_pixi_command(
        "run", "prek", "run", "--files", *str_files, check=False
    )
    if result.returncode != 0:
        print_console.fail(
            "Some files were not formatted successfully.\n"
            f"Run `pixi run prek run --files {' '.join(str_files)}` in the project root to see the details."
        )
        return

    print_console.step_done("Files formatted.")


def format_all_files_in_project(project_root: Path) -> None:
    """Run prek pre-commit hooks on all files in the project via pixi.

    Args:
        project_root: Project root directory (where pixi.toml / prek.toml live).
    """
    runner = PixiRunner(project_root=project_root)
    print_console.step("Formatting files ...")
    result = runner.run_pixi_command("run", "prek", "run", "--all-files", check=False)

    if result.returncode != 0:
        print_console.fail(
            "Some files were not formatted successfully.\n"
            "Run `pixi run prek run --all-files` in the project root to see the details."
        )
        return

    print_console.step_done("Files formatted.")
