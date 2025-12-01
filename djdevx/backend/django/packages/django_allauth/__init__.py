import typer

from .account import app as account_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    account_app,
    name="account",
    help="Manage django-allauth with account functionality",
)
