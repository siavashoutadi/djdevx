import typer

from .all import app as all_packages
from .whitenoise import app as whitenoise
from .django_browser_reload import app as browser_reload
from .django_debug_toolbar import app as debug_toolbar
from .django_tailwind_cli import app as tailwind_cli
from .django_health_check import app as healthcheck
from .django_storages import app as storages
from .django_anymail import app as anymail
from .django_allauth import app as allauth
from .djangorestframework import app as djangorestframework
from .django_oauth_toolkit import app as oauth_toolkit
from .drf_spectacular import app as drf_spectacular
from .django_auditlog import app as auditlog
from .django_guardian import app as guardian
from .django_role_permissions import app as roles
from .django_cors_headers import app as cors
from .django_filter import app as filter
from .drf_nested_routers import app as nested_routers


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    all_packages,
    name="all",
    help="Manage all packages at once",
)
app.add_typer(
    allauth,
    name="django-allauth",
    help="Manage django-allauth package",
)
app.add_typer(
    anymail,
    name="django-anymail",
    help="Manage django-anymail package",
)
app.add_typer(
    auditlog,
    name="django-auditlog",
    help="Manage django-auditlog package",
)
app.add_typer(
    browser_reload,
    name="django-browser-reload",
    help="Manage django-browser-reload package",
)
app.add_typer(
    cors,
    name="django-cors-headers",
    help="Manage django-cors-headers package",
)
app.add_typer(
    debug_toolbar,
    name="django-debug-toolbar",
    help="Manage django-debug-toolbar package",
)
app.add_typer(
    filter,
    name="django-filter",
    help="Manage django-filter package",
)
app.add_typer(
    guardian,
    name="django-guardian",
    help="Manage django-guardian package",
)
app.add_typer(
    healthcheck,
    name="django-health-check",
    help="Manage django-health-check package",
)
app.add_typer(
    oauth_toolkit,
    name="django-oauth-toolkit",
    help="Manage django-oauth-toolkit package",
)
app.add_typer(
    roles,
    name="django-role-permissions",
    help="Manage django-role-permissions package",
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
app.add_typer(
    djangorestframework,
    name="djangorestframework",
    help="Manage djangorestframework package",
)
app.add_typer(
    nested_routers,
    name="drf-nested-routers",
    help="Manage drf-nested-routers package",
)
app.add_typer(
    drf_spectacular,
    name="drf-spectacular",
    help="Manage drf-spectacular package",
)
app.add_typer(
    whitenoise,
    name="whitenoise",
    help="Manage whitenoise package",
)
