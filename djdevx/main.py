import typer

from .version import app as version_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app)

if __name__ == "__main__":
    app()
