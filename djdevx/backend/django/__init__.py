import typer

from .packages import app as packages_app
from .feature import app as feature_app
from .create import app as create_app
from .list import app as list_app
from .database import app as database_app
from .cache import app as cache_app
from .settings import app as settings_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    packages_app, name="packages", help="Install and configure django packages"
)
app.add_typer(feature_app, name="feature", help="Add features to your Django project")
app.add_typer(
    create_app, name="create", help="Create new Django applications or components"
)
app.add_typer(list_app, name="list", help="List installed Django packages and features")
app.add_typer(database_app, name="database", help="Manage database infrastructure")
app.add_typer(cache_app, name="cache", help="Manage cache infrastructure")
app.add_typer(
    settings_app, name="settings", help="Manage project secrets and config vars"
)
