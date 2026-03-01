from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-import-export
    """
    pm = DjangoProjectManager()

    print_console.step("Installing django-import-export package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-import-export")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django-import-export"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    print_console.success("django-import-export is installed successfully.")


@app.command()
def remove():
    """
    Remove django-import-export package
    """
    print_console.step("Removing django-import-export package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-import-export"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-import-export")

    url_path = Path.joinpath(pm.packages_urls_path, "django_import_export.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_import_export.py")
    settings_url.unlink(missing_ok=True)
