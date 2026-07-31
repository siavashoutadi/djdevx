"""djdevx CLI — main entry point."""

import typer

from .deployment import app as deploy_app
from .version import app as version_app
from .requirement import app as requirement_app
from .new import app as new_app
from .packages import app as packages_app
from .frameworks import app as frameworks_app
from .features import app as features_app
from .create import app as create_app
from .database import app as database_app
from .cache import app as cache_app
from .settings import app as settings_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app, name="version", help="Show the application version")
app.add_typer(requirement_app, name="requirement", help="Check system requirements")
app.add_typer(new_app, name="new", help="Create a new project")
app.add_typer(packages_app, name="packages", help="Manage Django packages")
app.add_typer(frameworks_app, name="frameworks", help="Manage CSS/JS frameworks")
app.add_typer(features_app, name="features", help="Manage features")
app.add_typer(create_app, name="create", help="Create new Django applications")
app.add_typer(database_app, name="database", help="Manage database infrastructure")
app.add_typer(cache_app, name="cache", help="Manage cache infrastructure")
app.add_typer(settings_app, name="settings", help="Manage project secrets and configs")
app.add_typer(deploy_app, name="deployment", help="Generate deployment manifests")

if __name__ == "__main__":
    app()
