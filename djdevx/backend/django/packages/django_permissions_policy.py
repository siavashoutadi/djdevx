from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-permissions-policy
    """
    pm = DjangoProjectManager()

    console.step("Installing django-permissions-policy package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-permissions-policy")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django-permissions-policy"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-permissions-policy is installed successfully.")


@app.command()
def remove():
    """
    Remove django-permissions-policy package
    """
    console.step("Removing django-permissions-policy package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-permissions-policy"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-permissions-policy")

    url_path = Path.joinpath(pm.packages_urls_path, "django_permissions_policy.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(
        pm.packages_settings_path, "django_permissions_policy.py"
    )
    settings_url.unlink(missing_ok=True)

    console.success("django-permissions-policy is removed successfully.")
