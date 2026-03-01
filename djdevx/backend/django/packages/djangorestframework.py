from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure djangorestframework
    """
    pm = DjangoProjectManager()

    print_console.step("Installing djangorestframework package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("djangorestframework")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "djangorestframework"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    print_console.success("djangorestframework is installed successfully.")


@app.command()
def remove():
    """
    Remove djangorestframework
    """
    print_console.step("Removing djangorestframework package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("djangorestframework"):
        uv_runner.remove_package("djangorestframework")

    url_path = Path.joinpath(pm.packages_urls_path, "djangorestframework.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "djangorestframework.py")
    settings_url.unlink(missing_ok=True)

    print_console.success("djangorestframework is removed successfully.")
