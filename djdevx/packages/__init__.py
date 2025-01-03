import typer

from .django_browser_reload import app as browser_reload
from .whitenoise import app as whitenoise

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    browser_reload,
    name="django-browser-reload",
    help="Manage django-browser-reload package",
)
app.add_typer(
    whitenoise,
    name="whitenoise",
    help="Manage whitenoise package",
)
