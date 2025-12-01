import typer

from .packages import app as packages_app
from .feature import app as feature_app
from .create import app as create_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    packages_app, name="packages", help="Install and configure django packages"
)
app.add_typer(feature_app, name="feature", help="Add features to your Django project")
app.add_typer(
    create_app, name="create", help="Create new Django applications or components"
)
