import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-auditlog
    """
    pm = DjangoProjectManager()

    console.step("Installing django-auditlog package ...")

    uv = UvRunner()
    uv.add_package("django-auditlog")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-auditlog"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-auditlog is installed successfully.")


@app.command()
def remove():
    """
    Remove django-auditlog
    """
    console.step("Removing django-auditlog package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-auditlog"):
        uv.remove_package("django-auditlog")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_auditlog.py")
    settings_path.unlink(missing_ok=True)

    console.success("django-auditlog is removed successfully.")
