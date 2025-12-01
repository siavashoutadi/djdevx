from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-csp
    """
    pm = DjangoProjectManager()

    console.step("Installing django-csp package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-csp")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-csp"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-csp is installed successfully.")


@app.command()
def remove():
    """
    Remove django-csp package
    """
    console.step("Removing django-csp package ...")
    pm = DjangoProjectManager()
    if pm.has_dependency("django-csp"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-csp")

    url_path = Path.joinpath(pm.packages_urls_path, "django_csp.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_csp.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-csp is removed successfully.")
