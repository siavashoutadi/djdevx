"""ddx profiles — create and manage project profiles."""

import typer
from pathlib import Path
from typing import Annotated, Optional

from djdevx.core.console import print_console
from ..utils.console import prompts

from .loader import list_builtin_profiles
from .writer import (
    create_profile_interactive,
    generate_profile_from_project,
    write_answers_toml,
    write_profile_toml,
)

app = typer.Typer(no_args_is_help=True)


@app.command(name="create")
def create(
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output file path for the profile (default: ddx-profile.toml)",
        ),
    ] = None,
    from_project: Annotated[
        bool,
        typer.Option(
            "--from-project",
            help="Generate the profile from the current project instead of prompting",
        ),
    ] = False,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            help="Build the profile interactively instead of prompting",
        ),
    ] = False,
) -> None:
    """Create a project profile interactively or from the current project."""
    if from_project:
        _create_from_project(output)
        return

    if not interactive:
        project_root = _find_project_root()
        if project_root is not None:
            generate = prompts.confirm(
                "Generate a profile from the current project?", default=True
            )
            if generate is None:
                raise typer.Abort()
            if generate:
                _create_from_project(output)
                return

    _create_interactive(output)


def _find_project_root() -> Optional[Path]:
    """Return the nearest djdevx project root, or None if not inside one."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "djdevx.toml").exists():
            return current
        current = current.parent
    return None


def _resolve_output(output: Optional[Path]) -> Path:
    """Prompt for the profile file name when none is given."""
    if output is not None:
        return output
    raw = prompts.text("Profile file name:", default="ddx-profile.toml")
    if raw is None:
        raise typer.Abort()
    return Path(raw)


def _create_from_project(output: Optional[Path]) -> None:
    """Generate and write a profile from the current project state."""
    project_root = _find_project_root()
    if project_root is None:
        print_console.fail(
            "Could not find a djdevx.toml. Are you in a project managed by djdevx?"
        )
        raise typer.Exit(code=1)

    output = _resolve_output(output)
    print_console.step("Building your profile ...")
    profile = generate_profile_from_project(project_root)

    write_profile_toml(profile, output)
    print_console.ok(f"Profile written to {output}")
    print_console.step_done(
        "Profile ready. Use it with: ddx new --profile " + str(output)
    )


def _create_interactive(output: Optional[Path]) -> None:
    """Interactively build and write a profile (and optional answers)."""
    output = _resolve_output(output)
    print_console.step("Building your profile ...")
    profile, answers = create_profile_interactive()

    write_profile_toml(profile, output)
    print_console.ok(f"Profile written to {output}")

    builtins = list_builtin_profiles()
    if builtins:
        print_console.info("Built-in profiles available: " + ", ".join(builtins))

    if answers:
        answers_path = output.with_name(
            f"ddx-answers-{output.stem.removeprefix('ddx-profile-')}.toml"
            if output.stem.startswith("ddx-profile-")
            else f"ddx-answers-{output.stem}.toml"
        )
        write_answers = prompts.confirm(
            "Also generate an answers file with the collected values?",
            default=True,
        )
        if write_answers is None:
            raise typer.Abort()
        if write_answers:
            write_answers_toml(answers, answers_path)
            print_console.ok(f"Answers written to {answers_path}")

    print_console.step_done(
        "Profile ready. Use it with: ddx new --profile " + str(output)
    )


@app.command(name="list")
def list_cmd() -> None:
    """List available built-in profiles."""
    names = list_builtin_profiles()
    if not names:
        print_console.info("No built-in profiles available.")
        return
    with print_console.table(
        "Profiles",
        [("Name", {"no_wrap": True})],
    ) as tbl:
        for name in names:
            tbl.add_row(name)
    print_console.info("Use with: ddx new --profile <name>")
