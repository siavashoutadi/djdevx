import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-extensions
    """
    pm = DjangoProjectManager()

    console.step("Installing django-extensions package ...")

    uv = UvRunner()
    uv.add_package("django-extensions")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django_extensions"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-extensions is installed successfully.")


@app.command()
def remove():
    """
    Remove django-extensions
    """
    console.step("Removing django-extensions package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-extensions"):
        uv.remove_package("django-extensions")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_extensions.py")
    settings_path.unlink(missing_ok=True)

    console.success("django-extensions is removed successfully.")
