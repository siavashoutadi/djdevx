import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-silk
    """
    pm = DjangoProjectManager()

    console.step("Installing django-silk package ...")

    uv = UvRunner()
    uv.add_package("django-silk", group="dev")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django_silk"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-silk is installed successfully.")


@app.command()
def remove():
    """
    Remove django-silk
    """
    console.step("Removing django-silk package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-silk", "dev"):
        uv.remove_package("django-silk", group="dev")

    url_path = Path.joinpath(pm.packages_urls_path, "django_silk.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_silk.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-silk is removed successfully.")
