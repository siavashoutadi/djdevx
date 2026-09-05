"""Requirement check — verifies system tools are installed."""

import subprocess
import sys
from typing import Annotated, Optional

import typer

from ..utils.console import prompts
from djdevx.core.console import print_console
from ..utils.system.tools import system_tools

app = typer.Typer(no_args_is_help=True)

REQUIRED_TOOLS = ("pixi", "git", "docker")

PIXI_INSTALL_URL = "https://pixi.prefix.dev/latest/installation/"
GIT_INSTALL_URL = "https://git-scm.com/downloads"
DOCKER_INSTALL_URL = "https://docs.docker.com/get-docker/"
DOCKER_MAC_INSTALL_URL = "https://docs.docker.com/desktop/setup/install/mac-install/"
HOMEBREW_INSTALL_URL = "https://brew.sh"


def _autocomplete_tool(incomplete: str) -> list[str]:
    return [tool for tool in REQUIRED_TOOLS if tool.startswith(incomplete)]


def _linux_package_manager() -> Optional[str]:
    for manager in ("apt-get", "dnf", "pacman", "zypper"):
        if system_tools.is_tool_installed(manager):
            return manager
    return None


def _linux_git_commands(manager: str) -> list[str]:
    if manager == "apt-get":
        return ["sudo apt-get update", "sudo apt-get install -y git"]
    if manager == "dnf":
        return ["sudo dnf install -y git"]
    if manager == "pacman":
        return ["sudo pacman -S --noconfirm git"]
    if manager == "zypper":
        return ["sudo zypper --non-interactive install git"]
    return []


def _install_commands(tool: str) -> list[str]:
    """Return the shell commands needed to install a tool on this platform."""
    if sys.platform == "darwin":
        if tool == "pixi":
            return ["curl -fsSL https://pixi.sh/install.sh | bash"]
        if system_tools.is_tool_installed("brew"):
            if tool == "git":
                return ["brew install git"]
            if tool == "docker":
                return ["brew install --cask docker"]
            return []
        return []
    if sys.platform == "linux":
        if tool == "pixi":
            return ["curl -fsSL https://pixi.sh/install.sh | bash"]
        if tool == "docker":
            return ["curl -fsSL https://get.docker.com | sudo sh"]
        if tool == "git":
            manager = _linux_package_manager()
            return _linux_git_commands(manager) if manager else []
        return []
    return []


def _install_tool_guide(tool: str) -> str:
    if sys.platform == "darwin" and not system_tools.is_tool_installed("brew"):
        if tool == "docker":
            return (
                f"Homebrew is required to install Docker on macOS. "
                f"Install it from {HOMEBREW_INSTALL_URL}, then run this command again. "
                f"Installation guide: {DOCKER_MAC_INSTALL_URL}"
            )
        return (
            f"Homebrew is required to install {tool} on macOS. "
            f"Install it from {HOMEBREW_INSTALL_URL}, then run this command again."
        )
    if tool == "docker":
        return f"Installation guide: {DOCKER_INSTALL_URL}"
    if tool == "git":
        return f"Installation guide: {GIT_INSTALL_URL}"
    return f"Installation guide: {PIXI_INSTALL_URL}"


@app.command()
def verify():
    """Check the requirements for project creation."""
    with print_console.step_group(
        "Checking the requirements ...", done="All requirements are met!"
    ) as step:
        pixi_installed = system_tools.is_tool_installed("pixi")
        if pixi_installed:
            step.ok("pixi is installed")
        else:
            step.fail(f"pixi is not installed - {PIXI_INSTALL_URL}")

        git_installed = system_tools.is_tool_installed("git")
        if git_installed:
            step.ok("git is installed")
        else:
            step.fail(f"git is not installed - {GIT_INSTALL_URL}")

        docker_installed = system_tools.is_tool_installed("docker")
        if docker_installed:
            step.ok("Docker is installed")
        else:
            step.fail(f"Docker is not installed - {DOCKER_INSTALL_URL}")

        if not (docker_installed and pixi_installed and git_installed):
            step.fail(
                "Some requirements are missing. Please follow the links above to install them."
            )
            raise typer.Exit(code=1)


@app.command()
def install(
    tool: Annotated[
        Optional[str],
        typer.Option(
            "--tool",
            "-t",
            help="Tool to install (pixi, git, docker). If omitted, prompts.",
            autocompletion=_autocomplete_tool,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print commands without running them."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print each command before running it."),
    ] = False,
) -> None:
    """Install the required tools for project creation."""
    if sys.platform not in ("darwin", "linux"):
        print_console.fail(
            f"Unsupported platform '{sys.platform}'. "
            "This command supports Linux and macOS only."
        )
        raise typer.Exit(code=1)

    if tool is not None:
        if tool not in REQUIRED_TOOLS:
            print_console.fail(
                f"Unknown tool '{tool}'. Choose from: {', '.join(REQUIRED_TOOLS)}."
            )
            raise typer.Exit(code=1)
        selected = [tool]
    else:
        missing = [
            name for name in REQUIRED_TOOLS if not system_tools.is_tool_installed(name)
        ]
        if not missing:
            print_console.step_done("All required tools are already installed.")
            raise typer.Exit()
        choices = [
            prompts.Choice(title=name, value=name, checked=True) for name in missing
        ]
        selected = prompts.checkbox("Select tools to install:", choices=choices)
        if not selected:
            print_console.info("No tools selected.")
            raise typer.Exit()

    failed = False
    for name in selected:
        if system_tools.is_tool_installed(name):
            print_console.ok(f"{name} is already installed.")
            continue
        commands = _install_commands(name)
        if not commands:
            print_console.fail(
                f"Cannot install {name} on this system. {_install_tool_guide(name)}"
            )
            failed = True
            continue
        with print_console.step_group(
            f"Installing {name} ...", done=f"{name} is installed successfully."
        ) as step:
            install_failed = False
            for command in commands:
                if verbose or dry_run:
                    step.info(f"$ {command}")
                if dry_run:
                    continue
                result = subprocess.run(command, shell=True)
                if result.returncode != 0:
                    step.fail(f"Failed to install {name}.")
                    failed = True
                    install_failed = True
                    break
            if not install_failed and not dry_run:
                step.done()
            elif dry_run and not install_failed:
                step.ok(f"{name} would be installed.")
                step.done()

    if failed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
