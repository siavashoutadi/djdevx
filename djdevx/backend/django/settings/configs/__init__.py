"""
ddx backend django settings configs — manage config variables.

Commands:
  init prod    Prompt for required config vars and write .env.prod.
  list dev     Table of config vars with source (dev resolve chain).
  list prod    Table of config vars with source (prod resolve chain).
  verify dev   Exit 1 if any config var without dev default missing.
  verify prod  Exit 1 if any config var missing from .env.prod.
"""

import typer

from .init import app as init_app
from .list import app as list_app
from .verify import app as verify_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(init_app, name="init", help="Initialise configs for prod")
app.add_typer(list_app, name="list", help="List config vars with source and value")
app.add_typer(verify_app, name="verify", help="Verify config vars are present")
