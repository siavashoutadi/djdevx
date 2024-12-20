import typer
from djdevx import __version__

app = typer.Typer()


@app.command()
def version():
    """
    Show the application version.
    """
    typer.echo(__version__)


if __name__ == "__main__":
    app()
