import typer
from djdevx import __version__

app = typer.Typer()


@app.callback(invoke_without_command=True)
def version():
    """
    Show the application version.
    """
    typer.echo(__version__)


if __name__ == "__main__":
    app()
