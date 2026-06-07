"""PostgreSQL database management."""

from pathlib import Path
import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.devcontainer import ServiceConfig, VolumeConfig
from ....utils.djdevx_config.backend import DatabaseTracker
from ....utils.templates.manager import TemplateManager


POSTGRES_ENV_VARIABLES = {
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_DB": "postgres",
    "PGDATA": "/var/lib/postgresql/data/pgdata",
}
POSTGRES_DEPENDENCY = "psycopg2-binary"
POSTGRES_DOCKER_SERVICE: ServiceConfig = {
    "name": "db",
    "image": "postgres:16",
    "environment": POSTGRES_ENV_VARIABLES,
    "volumes": ["app-db-data:/var/lib/postgresql/data/pgdata"],
    "networks": ["devcontainer"],
}

POSTGRES_VOLUMES: list[VolumeConfig] = [
    {
        "name": "app-db-data",
        "driver": "local",
    }
]

PGADMIN_DOCKER_SERVICE: ServiceConfig = {
    "name": "pgadmin",
    "image": "dpage/pgadmin4:latest",
    "environment": {
        "PGADMIN_DEFAULT_EMAIL": "admin@example.com",
        "PGADMIN_DEFAULT_PASSWORD": "admin",
    },
    "volumes": ["pgadmin-data:/var/lib/pgadmin"],
    "networks": ["devcontainer"],
    "ports": ["80"],
    "depends_on": ["db"],
}

PGADMIN_VOLUMES: list[VolumeConfig] = [
    {
        "name": "pgadmin-data",
        "driver": "local",
    },
    {
        "name": "pgadmin-config",
        "driver": "local",
    },
]

app = typer.Typer(no_args_is_help=True)


@app.command()
def install() -> None:
    """Install PostgreSQL database."""
    pm = DjangoProjectManager()
    pm.add_dependency(POSTGRES_DEPENDENCY)

    current_dir = Path(__file__).resolve().parent

    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "database"
        / "postgres"
    )

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir,
        dest_dir=pm.project_path.parent,
        template_context={"backend_root": str(pm.project_path)},
    )

    pm.add_service_to_docker_compose(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
    pm.add_service_to_docker_compose(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)

    tracker = DatabaseTracker()
    tracker.write_database_config("postgres", "postgres")

    print_console.success("PostgreSQL database installed successfully!")


@app.command()
def remove() -> None:
    """Remove PostgreSQL database."""

    pm = DjangoProjectManager()

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "new"
        / "backend"
        / "django"
        / "{{backend_root}}"
        / "settings"
        / "django"
        / "database.py"
    )

    pm.copy_template(source_file=source_dir, dest_dir=pm.django_settings_path)

    pm.remove_dependency(POSTGRES_DEPENDENCY)

    pm.remove_service_from_docker_compose(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
    pm.remove_service_from_docker_compose(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)

    DatabaseTracker().remove_database_config("postgres")

    print_console.success("PostgreSQL database removed successfully!")
