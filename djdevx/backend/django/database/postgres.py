"""PostgreSQL database management."""

from pathlib import Path
import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.devcontainer import ServiceConfig, VolumeConfig


POSTGRES_ENV_VARIABLES = {
    "POSTGRES_SERVER": "db",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_DB": "postgres",
    "PGDATA": "/var/lib/postgresql/data/pgdata",
}
POSTGRES_DEPENDENCY = "psycopg2-binary"
POSTGRES_DOCKER_SERVICE: ServiceConfig = {
    "name": "db",
    "image": "postgres:16",
    "env_file": ["./.env/postgres"],
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
    "env_file": ["./.env/pgadmin"],
    "volumes": ["pgadmin-data:/var/lib/pgadmin"],
    "networks": ["devcontainer"],
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

    context = {key.lower(): value for key, value in POSTGRES_ENV_VARIABLES.items()}
    pm.copy_templates(source_dir, context)

    for key, value in POSTGRES_ENV_VARIABLES.items():
        pm.add_env_variable(key, value, pm.devcontainer_env_devcontainer_path)

    pm.add_service_to_docker_compose(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
    pm.add_service_to_docker_compose(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)

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

    pm.remove_env_file("postgres")
    pm.remove_env_file("pgadmin")

    for env in POSTGRES_ENV_VARIABLES:
        pm.remove_env_variable(env, pm.devcontainer_env_devcontainer_path)

    pm.remove_dependency(POSTGRES_DEPENDENCY)

    pm.remove_service_from_docker_compose(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
    pm.remove_service_from_docker_compose(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)

    print_console.success("PostgreSQL database removed successfully!")
