"""PostgreSQL database provider."""

import shutil

from .._base import BaseDatabase
from .._registry import register
from ...utils.devcontainer import ServiceConfig, VolumeConfig, DockerComposeManager
from ...utils.services import PostgresService
from ...utils.types.pixi_types import PixiPackageSpec

POSTGRES_ENV_VARIABLES = {
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_DB": "postgres",
    "PGDATA": "/var/lib/postgresql/data/pgdata",
}
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


@register
class PostgresDatabase(BaseDatabase):
    name: str = "postgres"
    display_name: str = "PostgreSQL"
    description: str = "PostgreSQL database provider for Django projects."
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="psycopg2-binary", kind="conda"),
        PixiPackageSpec(name="postgresql", kind="conda", pixi_feature="dev"),
    ]
    restore_on_remove: dict[str, str] = {
        "settings/django/database.py": "settings/django/database.py"
    }

    def after_pixi_install(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
        compose.add_service(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)

    def after_pixi_remove(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(POSTGRES_DOCKER_SERVICE, POSTGRES_VOLUMES)
        compose.remove_service(PGADMIN_DOCKER_SERVICE, PGADMIN_VOLUMES)
        self._wipe_dev_data()

    def _wipe_dev_data(self) -> None:
        service = PostgresService(self.structure.root)
        try:
            if service.is_up():
                service.down()
        except OSError:
            pass
        shutil.rmtree(service.data_dir, ignore_errors=True)
