# Adding a Database

Step-by-step guide to adding a new database provider to djdevx. Databases
manage database providers with Docker Compose integration. Only **one**
database can be installed at a time — the CLI enforces this.

This page focuses on database-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Database pattern](#database-pattern)
2. [Docker Compose structure](#docker-compose-structure)
3. [Templates directory](#templates-directory)
4. [Single-instance constraint](#single-instance-constraint)
5. [CLI commands](#cli-commands)
6. [Testing](#testing)

---

## Database pattern

Databases do **not** override `install()` and `remove()`. They use lifecycle
hooks — `after_pixi_install()` / `after_pixi_remove()` add and remove the
Docker Compose services, and `restore_on_remove` restores the default
`database.py` settings file from `djdevx/new/templates/`:

```python
# djdevx/database/postgres/__init__.py
from .._base import BaseDatabase
from .._registry import register
from ...utils.devcontainer import ServiceConfig, VolumeConfig, DockerComposeManager
from ...utils.types.pixi_types import PixiPackageSpec


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
```

Note the two pixi deps: the runtime driver (`psycopg2-binary`) plus a
dev-only dependency (`postgresql` with `pixi_feature="dev"`).

Because the provider overwrites `settings/django/database.py`, removal must
restore the original sqlite default. `restore_on_remove` maps the project
path to the template under `djdevx/new/templates/` — see
[Reverting from the new template](adding-a-package.md#reverting-from-the-new-template-restore_on_remove).
`cleanup_files()` deletes the generated postgres `database.py`, then
`restore_original_templates()` re-copies the default.

## Docker Compose structure

Define Docker service configs as module-level constants — `ServiceConfig`
(name, image, environment, volumes, networks, ports, depends_on) and
`VolumeConfig` (name, driver):

```python
POSTGRES_DOCKER_SERVICE: ServiceConfig = {
    "name": "db",
    "image": "postgres:16",
    "environment": {
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_DB": "postgres",
        "PGDATA": "/var/lib/postgresql/data/pgdata",
    },
    "volumes": ["app-db-data:/var/lib/postgresql/data/pgdata"],
    "networks": ["devcontainer"],
}

POSTGRES_VOLUMES: list[VolumeConfig] = [
    {"name": "app-db-data", "driver": "local"},
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
```

You can add more than one service — postgres ships a `pgadmin` admin UI
alongside the `db` service. Use `DockerComposeManager` to add/remove services
in hooks.

## Templates directory

```
djdevx/database/<name>/
├── __init__.py
└── templates/
    └── settings/
        └── django/
            └── database.py.j2         # → settings/django/database.py
```

## Single-instance constraint

The add command checks if a database is already installed and blocks adding
a second one:

```
$ ddx database add mysql
A database (postgres) is already installed. Only one database can be installed at a time.
```

## CLI commands

```
ddx database add [NAME] [-v]
ddx database remove [NAME] [-v]
ddx database list
```

## Testing

```bash
ddx database add postgres
ddx database list
ddx database remove postgres
```

Verify Docker Compose configuration:

```bash
cat .devcontainer/docker-compose.yaml
```

See [Testing](creating-an-installable.md#testing) for the CLI integration
test pattern and golden-file fixtures.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Database Architecture](database-architecture.md) — BaseDatabase details
- [Installable System](installable-system.md) — Shared infrastructure
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
