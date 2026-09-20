"""Format output files using prek pre-commit hooks via pixi."""

from pathlib import Path

from djdevx.core.process import PixiRunner
from djdevx.core.console import print_console, NestedStep


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
    if not _is_stable(result, runner, "run", "prek", "run", "--files", *str_files):
        _report_failure(
            f"Run `pixi run prek run --files {' '.join(str_files)}` in the project root to see the details.",
            step=step,
        )
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

    if not _is_stable(result, runner, "run", "prek", "run", "--all-files"):
        _report_failure(
            "Run `pixi run prek run --all-files` in the project root to see the details.",
            step=step,
        )
        return

    if step is not None:
        step.ok("Files formatted.")
    else:
        print_console.step_done("Files formatted.")


def _is_stable(first_result, runner: PixiRunner, *args) -> bool:
    """Whether a prek run leaves the tree formatted.

    prek returns non-zero when a hook modifies files (fixers like ruff
    format or end-of-file-fixer). A non-zero first run is therefore
    expected the first time formatting is applied; a second run confirms
    whether the working tree is now stable.
    """
    if first_result.returncode == 0:
        return True
    rerun = runner.run_pixi_command(*args, check=False)
    return rerun.returncode == 0


def _report_failure(message: str, step: NestedStep | None = None) -> None:
    """Surface a remaining formatting failure to the user."""
    full = f"Some files were not formatted successfully.\n{message}"
    if step is not None:
        step.info(message)
    else:
        print_console.fail(full)
