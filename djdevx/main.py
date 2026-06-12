import typer

from .deployment import app as deploy_app
from .version import app as version_app
from .requirement import app as requirement_app
from .new import app as new_app
from .backend import app as backend_app


app = typer.Typer(no_args_is_help=True)

app.add_typer(version_app)
app.add_typer(requirement_app)
app.add_typer(new_app, name="new", help="Create a new project")
app.add_typer(backend_app, name="backend", help="Backend development tools")
app.add_typer(deploy_app, name="deployment", help="Generate deployment manifests")

if __name__ == "__main__":
    app()
