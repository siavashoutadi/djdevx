import subprocess
import typer
from pathlib import Path

from ..utils.print_console import (
    print_step,
    print_success,
    print_error,
    print_warning,
    print_list,
    print_info,
)

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


def get_multi_option_packages_names() -> set:
    current_dir = Path(__file__).parent
    return set(
        [
            str(file.stem)
            for file in current_dir.iterdir()
            if file.is_dir() and file.name not in ["__pycache__"]
        ]
    )


@app.command()
def install():
    """
    Install and configure all available packages
    """
    print_step("Installing all packages...\n")

    multi_option_packages = get_multi_option_packages_names()
    try:
        for pkg in get_all_packages_names():
            if pkg not in multi_option_packages:
                subprocess.check_call(["ddx", "packages", pkg, "install"])
            print_info("\n")

    except Exception as e:
        print_error(f"Error installing packages: {str(e)}")
        raise typer.Exit(code=1)

    print_warning(
        "More options are required form the user to be able to install the following packages. Try to install them manually."
    )
    print_list(pkg.replace("_", "-") for pkg in multi_option_packages)


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
