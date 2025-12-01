import shutil
import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.file_operations import TemplateManager
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def env():
    """
    Creating environment variables for channels
    """
    pm = DjangoProjectManager()

    console.step("Creating environment variables for channels ...")
    pm.add_env_variable(
        key="CHANNEL_LAYERS_REDIS_HOST",
        value="redis://default:${REDIS_PASSWORD}@cache:6379/1",
    )

    console.success("channels environment variables are configured successfully.")


@app.command()
def install():
    """
    Install and configure channels
    """
    pm = DjangoProjectManager()

    console.step("Installing channels package ...")

    uv = UvRunner()
    uv.add_package("channels[daphne]")
    uv.add_package("channels_redis")
    uv.add_package("twisted[http2,tls]", group="dev")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent.parent / "templates" / "django" / "channels"

    pm.copy_templates(source_dir=source_dir, template_context={})

    env()

    console.success("channels is installed successfully.")


@app.command()
def remove():
    """
    Remove channels package
    """
    console.step("Removing channels package ...")

    pm = DjangoProjectManager()

    uv = UvRunner()
    for dep in ["channels", "channels-redis"]:
        if pm.has_dependency(dep):
            uv.remove_package(dep)

    if pm.has_dependency("twisted", "dev"):
        uv.remove_package("twisted", group="dev")

    settings_url = Path.joinpath(pm.packages_settings_path, "channels.py")
    settings_url.unlink(missing_ok=True)

    ws_url_path = pm.ws_urls_path
    shutil.rmtree(ws_url_path, ignore_errors=True)

    pm.remove_env_variable("CHANNEL_LAYERS_REDIS_HOST")

    # Restore original ASGI file without channels
    current_dir = Path(__file__).resolve().parent
    template_asgi_path = (
        current_dir.parent.parent.parent
        / "templates"
        / "new"
        / "backend"
        / "django"
        / "{{backend_root}}"
        / "applications"
        / "asgi.py"
    )

    template_manager = TemplateManager()

    template_manager.copy_template(
        source_file=template_asgi_path,
        dest_dir=pm.project_path / "applications",
        template_context={"backend_root": "backend"},
    )

    console.success("channels is removed successfully.")
