import typer

from .version import app as version_app
from .requirement import app as requirement_app
from .init import app as init_app
from .packages import app as packages_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app)
app.add_typer(requirement_app)
app.add_typer(init_app)
app.add_typer(
    packages_app, name="packages", help="Install and configure django packages"
)

if __name__ == "__main__":
    app()
