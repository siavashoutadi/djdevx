import shutil
import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
from ..utils.project_info import has_dependency
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_settings_path,
    add_env_varibles,
    remove_env_varibles,
    copy_template_file,
    get_ws_url_path,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def env():
    """
    Creating environment variables for channels
    """
    is_project_exists_or_raise()

    print_step("Creating environment variables for channels ...")
    add_env_varibles(
        key="CHANNEL_LAYERS_REDIS_HOST",
        value="redis://default:${REDIS_PASSWORD}@cache:6379/1",
    )

    print_success("channels environment variables are configured successfully.")


@app.command()
def install():
    """
    Install and configure channels
    """
    is_project_exists_or_raise()

    print_step("Installing channels package ...")
    subprocess.check_call(["uv", "add", "channels[daphne]", "channels_redis"])
    subprocess.check_call(["uv", "add", "twisted[http2,tls]", "--group", "dev"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "channels"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    env()

    print_success("channels is installed successfully.")


@app.command()
def remove():
    """
    Remove channels package
    """
    print_step("Removing channels package ...")
    for dep in ["channels", "channels-redis"]:
        if has_dependency(dep):
            subprocess.check_call(["uv", "remove", dep])

    if has_dependency("twisted", "dev"):
        subprocess.check_call(["uv", "remove", "twisted", "--group", "dev"])

    settings_url = Path.joinpath(get_packages_settings_path(), "channels.py")
    settings_url.unlink(missing_ok=True)

    ws_url_path = get_ws_url_path()
    shutil.rmtree(ws_url_path)

    remove_env_varibles("CHANNEL_LAYERS_REDIS_HOST")

    current_dir = Path(__file__).resolve().parent
    source_file = current_dir.parent / "templates" / "init" / "applications" / "asgi.py"
    project_dir = get_project_path() / "applications"

    copy_template_file(
        source_file=source_file, dest_dir=project_dir, template_context={}
    )

    print_success("channels is removed successfully.")
