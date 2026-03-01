from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure whitenoise
    """
    pm = DjangoProjectManager()

    print_console.step("Installing whitenoise package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("whitenoise")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "whitenoise"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    print_console.success("whitenoise is installed successfully.")


@app.command()
def remove():
    """
    Remove whitenoise
    """
    print_console.step("Removing whitenoise package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("whitenoise"):
        uv_runner = UvRunner()
        uv_runner.remove_package("whitenoise")

    settings_url = Path.joinpath(pm.packages_settings_path, "whitenoise.py")
    settings_url.unlink(missing_ok=True)

    print_console.success("whitenoise is removed successfully.")
