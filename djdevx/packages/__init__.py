import typer

from .whitenoise import app as whitenoise
from .django_browser_reload import app as browser_reload
from .django_debug_toolbar import app as debug_toolbar


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    whitenoise,
    name="whitenoise",
    help="Manage whitenoise package",
)
app.add_typer(
    browser_reload,
    name="django-browser-reload",
    help="Manage django-browser-reload package",
)
app.add_typer(
    debug_toolbar,
    name="django-debug-toolbar",
    help="Manage django-debug-toolbar package",
)
