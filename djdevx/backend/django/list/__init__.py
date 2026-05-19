import typer

from .packages import list_packages
from .features import list_features
from .databases import list_databases

app = typer.Typer(no_args_is_help=True)

app.command(name="packages", help="List all installed Django packages")(list_packages)
app.command(name="features", help="List all installed Django features")(list_features)
app.command(name="databases", help="List all installed Django databases")(
    list_databases
)
