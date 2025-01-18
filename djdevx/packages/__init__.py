import typer

from .all import app as all_packages
from .whitenoise import app as whitenoise
from .django_browser_reload import app as browser_reload
from .django_debug_toolbar import app as debug_toolbar
from .django_tailwind_cli import app as tailwind_cli
from .django_health_check import app as healthcheck
from .django_storages import app as storages


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    all_packages,
    name="all",
    help="Manage all packages at once",
)
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
app.add_typer(
    healthcheck,
    name="django-health-check",
    help="Manage django-health-check package",
)
app.add_typer(
    storages,
    name="django-storages",
    help="Manage django-storages package",
)
app.add_typer(
    tailwind_cli,
    name="django-tailwind-cli",
    help="Manage django-tailwind-cli package",
)
