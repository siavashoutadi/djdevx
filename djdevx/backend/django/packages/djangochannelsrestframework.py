from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure djangochannelsrestframework
    """
    pm = DjangoProjectManager()
    if not pm.has_dependency("channels"):
        console.error(
            "'channels' package is a dependency for djangochannelsrestframework. Please install that frist."
        )
        console.info("\n> ddx packages channels install")
        raise typer.Exit(code=1)

    console.step("Installing djangochannelsrestframework package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("djangochannelsrestframework")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "djangochannelsrestframework"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("djangochannelsrestframework is installed successfully.")


@app.command()
def remove():
    """
    Remove djangochannelsrestframework package
    """
    console.step("Removing djangochannelsrestframework package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("djangochannelsrestframework"):
        uv_runner.remove_package("djangochannelsrestframework")

    settings_url = Path.joinpath(
        pm.packages_settings_path, "djangochannelsrestframework.py"
    )
    settings_url.unlink(missing_ok=True)

    console.success("djangochannelsrestframework is removed successfully.")
