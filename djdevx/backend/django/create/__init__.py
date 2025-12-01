import typer

from .app import startapp
from .admin import create_admin

app = typer.Typer(no_args_is_help=True)

app.command(name="app", help="Create a new Django application")(startapp)
app.command(name="admin", help="Create admin.py from model.py for an application")(
    create_admin
)
