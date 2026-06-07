"""
ddx backend django settings — manage project secrets and config variables.

Sub-commands:
  secrets   Manage secret fields (SecretStr) for dev and prod.
  configs   Manage config vars (non-secret settings) for dev and prod.
"""

import typer

from .secrets import app as secrets_app
from .configs import app as configs_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(secrets_app, name="secrets", help="Manage project secrets")
app.add_typer(configs_app, name="configs", help="Manage project config variables")
