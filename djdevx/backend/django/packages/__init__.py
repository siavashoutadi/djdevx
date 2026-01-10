import typer

from .whitenoise import app as whitenoise
from .django_browser_reload import app as browser_reload
from .django_debug_toolbar import app as debug_toolbar
from .django_extensions import app as extensions
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
from .django_meta import app as meta
from .drf_nested_routers import app as nested_routers
from .django_defender import app as defender
from .django_permissions_policy import app as permission_policy
from .django_csp import app as csp
from .django_simple_history import app as simple_history
from .django_snakeoil import app as snakeoil
from .drf_flex_fields import app as flex_fields
from .channels import app as channels_app
from .djangochannelsrestframework import app as channelrest
from .heroicons import app as heroicons
from .django_taggit import app as taggit


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    channels_app,
    name="channels",
    help="Manage channels package",
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
    csp,
    name="django-csp",
    help="Manage django-csp package",
)
app.add_typer(
    debug_toolbar,
    name="django-debug-toolbar",
    help="Manage django-debug-toolbar package",
)
app.add_typer(
    defender,
    name="django-defender",
    help="Manage django-defender package",
)
app.add_typer(
    extensions,
    name="django-extensions",
    help="Manage django-extensions package",
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
    meta,
    name="django-meta",
    help="Manage django-meta package",
)
app.add_typer(
    oauth_toolkit,
    name="django-oauth-toolkit",
    help="Manage django-oauth-toolkit package",
)
app.add_typer(
    permission_policy,
    name="django-permissions-policy",
    help="Manage django-permissions-policy package",
)
app.add_typer(
    roles,
    name="django-role-permissions",
    help="Manage django-role-permissions package",
)
app.add_typer(
    simple_history,
    name="django-simple-history",
    help="Manage django-simple-history package",
)
app.add_typer(
    snakeoil,
    name="django-snakeoil",
    help="Manage django-snakeoil package",
)
app.add_typer(
    storages,
    name="django-storages",
    help="Manage django-storages package",
)
app.add_typer(
    taggit,
    name="django-taggit",
    help="Manage django-taggit package",
)
app.add_typer(
    tailwind_cli,
    name="django-tailwind-cli",
    help="Manage django-tailwind-cli package",
)
app.add_typer(
    heroicons,
    name="heroicons",
    help="Manage heroicons package",
)
app.add_typer(
    channelrest,
    name="djangochannelsrestframework",
    help="Manage djangochannelsrestframework package",
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
    flex_fields,
    name="drf-flex-fields",
    help="Manage drf-flex-fields package",
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
