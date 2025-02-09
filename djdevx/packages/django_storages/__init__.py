import typer


from .install import app as install_packages
from .remove import remove_package
from .env import app as env_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    install_packages,
    name="install",
    help="Installing the django-storages for different backends",
)

app.add_typer(
    env_app,
    name="env",
    help="Setting up environment variables for django-storages package",
)

app.command(name="remove", help="Removing the django-storages package")(remove_package)
