# Database Architecture

Databases manage database providers (PostgreSQL, MySQL) with Docker Compose
integration. Only **one** database can be installed at a time — the CLI
enforces this automatically.

## BaseDatabase

`BaseDatabase` (`djdevx/database/_base.py`) extends `Installable` with
`section: str = "database"`. It adds no additional attributes — all behavior
comes from `Installable`.

### Single-Instance Constraint

The `add` command checks if a database is already installed and blocks adding
a second one:

```
$ ddx database add mysql
A database (postgres) is already installed. Only one database can be installed at a time.
```

### Hook-Based Pattern

Databases use lifecycle hooks for Docker Compose configuration — they do
**not** override `install()` and `remove()` directly:

```python
@register
class PostgresDatabase(BaseDatabase):
    name: str = "postgres"
    display_name: str = "PostgreSQL"
    description: str = "PostgreSQL database provider for Django projects."
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("psycopg2-binary")]
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

### Docker Service Configs

Define Docker Compose service configurations as module-level constants:

```python
from ...utils.devcontainer import ServiceConfig, VolumeConfig

POSTGRES_DOCKER_SERVICE: ServiceConfig = {
    "name": "db",
    "image": "postgres:16",
    "environment": {...},
    "volumes": ["app-db-data:/var/lib/postgresql/data/pgdata"],
    "networks": ["devcontainer"],
}

POSTGRES_VOLUMES: list[VolumeConfig] = [
    {"name": "app-db-data", "driver": "local"},
]
```

Use `DockerComposeManager` to add/remove services in the appropriate hooks.

### Concrete Example

The PostgreSQL provider (`djdevx/database/postgres/__init__.py`) demonstrates
the full pattern:

- Defines Docker service configs as module-level constants
- Uses `after_pixi_install()` to add services
- Uses `restore_on_remove` to restore the default `database.py` settings file
- Uses `after_pixi_remove()` to remove services

## CLI Commands

```
ddx database add [NAME] [-v]       # Install a database
ddx database remove [NAME] [-v]    # Remove a database
ddx database list                   # List all databases
```

The `add` command uses `prompts.select()` (single-choice) since only one
database can be installed.

## Native Dev Services

Databases can also run locally without Docker via `ddx dev`.
`utils/services/` owns the pixi-native `BaseDevService` implementations.
`utils/services/resolver.py` maps the installed provider (from tracking) to
its dev service: `SectionTracking("database").installed()` returns the single
installed name, which is looked up in the `name -> dev service` mapping.
Providers that add native dev support must register their service class in
`utils/services/resolver.py`.

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Database](adding-a-database.md) — Step-by-step guide
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
