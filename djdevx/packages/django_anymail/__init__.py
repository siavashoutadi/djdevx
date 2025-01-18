import typer

from .install import app as install_packages
from .remove import remove_package


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    install_packages,
    name="install",
    help="Installing the django-anymail package for different backends",
)

app.command(name="remove", help="Removing the django-anymail package")(remove_package)
