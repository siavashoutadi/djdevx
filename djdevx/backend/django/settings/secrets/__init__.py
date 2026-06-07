"""
ddx backend django settings secrets — manage secret fields.

Commands:
  init dev     Generate / prompt for all local .secrets/ entries.
  init prod    Generate / prompt for all .secrets.prod/ entries.
  list dev     Table of secrets with source (dev resolve chain).
  list prod    Table of secrets with source (prod resolve chain).
  verify dev   Exit 1 if any secret missing from .secrets/ with no dev default.
  verify prod  Exit 1 if any secret missing from .secrets.prod/.
"""

import typer

from .init import app as init_app
from .list import app as list_app
from .verify import app as verify_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(init_app, name="init", help="Initialise secrets for dev or prod")
app.add_typer(list_app, name="list", help="List secrets with source and value")
app.add_typer(verify_app, name="verify", help="Verify secrets are present")
