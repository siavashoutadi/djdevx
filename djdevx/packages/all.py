import subprocess
import typer
from pathlib import Path

from ..utils.print_console import print_step, print_success, print_error

app = typer.Typer(no_args_is_help=True)


def get_all_packages_names() -> set:
    current_dir = Path(__file__).parent
    return set(
        [
            str(file.stem).replace("_", "-")
            for file in current_dir.iterdir()
            if file.is_file() and file.name not in ["all.py", "__init__.py"]
        ]
    )


@app.command()
def install():
    """
    Install and configure all available packages
    """

    print_step("Installing all packages...\n")

    try:
        for pkg in get_all_packages_names():
            subprocess.check_call(["ddx", "packages", pkg, "install"])

        print_success("All packages are installed successfully.")
    except Exception as e:
        print_error(f"Error installing packages: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def remove():
    """
    Remove all packages
    """
    print_step("Removing all packages ...\n")

    try:
        for pkg in get_all_packages_names():
            subprocess.check_call(["ddx", "packages", pkg, "remove"])
        print_success("All packages are removed successfully.")
    except Exception as e:
        print_error(f"Error removing packages: {str(e)}")
        raise typer.Exit(code=1)
