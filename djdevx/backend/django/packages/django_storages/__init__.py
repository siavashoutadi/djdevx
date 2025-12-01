import typer

from .s3 import app as s3_app
from .azure import app as azure_app
from .google import app as google_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    s3_app,
    name="s3",
    help="Manage django-storages with S3 backend",
)

app.add_typer(
    azure_app,
    name="azure",
    help="Manage django-storages with Azure backend",
)

app.add_typer(
    google_app,
    name="google",
    help="Manage django-storages with Google backend",
)
