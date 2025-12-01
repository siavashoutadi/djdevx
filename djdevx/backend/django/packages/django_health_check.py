import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-health-check
    """
    pm = DjangoProjectManager()

    console.step("Installing django-health-check package ...")

    uv = UvRunner()
    uv.add_package("django-health-check")
    uv.add_package("psutil")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django_health_check"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-health-check is installed successfully.")


@app.command()
def remove():
    """
    Remove django-health-check
    """
    console.step("Removing django-health-check package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    for dep in ["django-health-check", "psutil"]:
        if pm.has_dependency(dep):
            uv.remove_package(dep)

    url_path = Path.joinpath(pm.packages_urls_path, "django_health_check.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_health_check.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-health-check is removed successfully.")
