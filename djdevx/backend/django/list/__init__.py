import typer

from .packages import list_packages
from .features import list_features

app = typer.Typer(no_args_is_help=True)

app.command(name="packages", help="List all installed Django packages")(list_packages)
app.command(name="features", help="List all installed Django features")(list_features)
