import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-taggit
    """
    pm = DjangoProjectManager()

    console.step("Installing django-taggit package ...")

    uv = UvRunner()
    uv.add_package("django-taggit")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-taggit"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-taggit is installed successfully.")


@app.command()
def remove():
    """
    Remove django-taggit
    """
    console.step("Removing django-taggit package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-taggit"):
        uv.remove_package("django-taggit")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_taggit.py")
    settings_path.unlink(missing_ok=True)

    console.success("django-taggit is removed successfully.")
