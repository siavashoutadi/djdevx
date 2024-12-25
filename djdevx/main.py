import typer

from .version import app as version_app
from .requirement import app as requirement_app
from .init import app as init_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app)
app.add_typer(requirement_app)
app.add_typer(init_app)

if __name__ == "__main__":
    app()
