"""Format output files using prek pre-commit hooks via pixi."""

from pathlib import Path

from ..project.pixi_runner import PixiRunner
from ..console.print import print_console, NestedStep


def format_files(
    files: list[Path], project_root: Path, step: NestedStep | None = None
) -> None:
    """Run prek pre-commit hooks on the given files via pixi.

    Args:
        files: List of absolute file paths to format.
        project_root: Project root directory (where pixi.toml / prek.toml live).
        step: Optional parent NestedStep to emit ``✓`` children into.
    """
    if not files:
        return
    runner = PixiRunner(project_root=project_root)
    str_files = [str(f) for f in files]
    if step is None:
        print_console.step("Formatting files ...")
    result = runner.run_pixi_command(
        "run", "prek", "run", "--files", *str_files, check=False
    )
    if result.returncode != 0:
        message = (
            "Some files were not formatted successfully.\n"
            f"Run `pixi run prek run --files {' '.join(str_files)}` in the project root to see the details."
        )
        if step is not None:
            step.info(
                "Run `pixi run prek run --files "
                f"{' '.join(str_files)}` in the project root to see the details."
            )
        else:
            print_console.fail(message)
        return

    if step is not None:
        step.ok("Files formatted.")
    else:
        print_console.step_done("Files formatted.")


def format_all_files_in_project(
    project_root: Path, step: NestedStep | None = None
) -> None:
    """Run prek pre-commit hooks on all files in the project via pixi.

    Args:
        project_root: Project root directory (where pixi.toml / prek.toml live).
        step: Optional parent NestedStep to emit ``✓`` children into.
    """
    runner = PixiRunner(project_root=project_root)
    if step is None:
        print_console.step("Formatting files ...")
    result = runner.run_pixi_command("run", "prek", "run", "--all-files", check=False)

    if result.returncode != 0:
        if step is not None:
            step.info(
                "Run `pixi run prek run --all-files` in the project root to see the details."
            )
        else:
            print_console.fail(
                "Some files were not formatted successfully.\n"
                "Run `pixi run prek run --all-files` in the project root to see the details."
            )
        return

    if step is not None:
        step.ok("Files formatted.")
    else:
        print_console.step_done("Files formatted.")
