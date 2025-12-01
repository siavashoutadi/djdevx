import typer

from .django import app as django_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(django_app, name="django", help="Django backend development tools")
