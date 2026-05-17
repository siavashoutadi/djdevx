import typer

from .redis import app as redis_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(redis_app, name="redis", help="Redis cache management")
