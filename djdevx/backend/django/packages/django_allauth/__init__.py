import typer

from .account import app as account_app
from .mfa import app as mfa_app
from .oidc_provider import app as oidc_provider_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    account_app,
    name="account",
    help="Manage django-allauth with account functionality",
)

app.add_typer(
    mfa_app,
    name="mfa",
    help="Manage django-allauth with MFA functionality",
)

app.add_typer(
    oidc_provider_app,
    name="oidc-provider",
    help="Manage django-allauth with OIDC provider functionality",
)
