# Adding a Cache

Step-by-step guide to adding a new cache provider to djdevx. Caches manage
cache providers (Redis) with Docker Compose integration. Only **one** cache
can be installed at a time — same constraint as databases.

This page focuses on cache-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Cache pattern](#cache-pattern)
2. [Restoring overridden files](#restoring-overridden-files)
3. [Templates directory](#templates-directory)
4. [Single-instance constraint](#single-instance-constraint)
5. [CLI commands](#cli-commands)
6. [Testing](#testing)

---

## Cache pattern

The same hook-based approach as databases: `after_pixi_install()` /
`after_pixi_remove()` manage the Docker Compose service:

```python
# djdevx/cache/redis/__init__.py
from .._base import BaseCache
from .._registry import register
from ...utils.devcontainer import ServiceConfig, VolumeConfig, DockerComposeManager
from ...utils.types.pixi_types import PixiPackageSpec

REDIS_DOCKER_SERVICE: ServiceConfig = {
    "name": "cache",
    "image": "redis:7.4-alpine",
    "environment": {"REDIS_PASSWORD": "redis_password"},
    "command": "/bin/sh -c 'redis-server --appendonly yes --requirepass $${REDIS_PASSWORD}'",
    "volumes": ["cache-data:/data"],
    "networks": ["devcontainer"],
}

REDIS_VOLUMES: list[VolumeConfig] = [
    {"name": "cache-data", "driver": "local"},
]


@register
class RedisCache(BaseCache):
    name: str = "redis"
    display_name: str = "Redis"
    description: str = "Redis cache with django-redis integration"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-redis")]
    restore_on_remove: dict[str, str] = {
        "settings/django/sessions.py": "settings/django/sessions.py"
    }

    def after_pixi_install(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)

    def after_pixi_remove(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)
```

## Restoring overridden files

The redis template overwrites `settings/django/sessions.py` (switching the
`SESSION_ENGINE` to `cached_db`). On uninstall the original must be restored
from `djdevx/new/templates/` — `restore_on_remove` maps
`project_rel → template_rel`:

```python
restore_on_remove: dict[str, str] = {
    "settings/django/sessions.py": "settings/django/sessions.py"
}
```

See [Reverting from the new template](adding-a-package.md#reverting-from-the-new-template-restore_on_remove)
for the full explanation.

## Templates directory

```
djdevx/cache/<name>/
├── __init__.py
└── templates/
    └── settings/
        └── django/
            └── caches.py.j2           # → settings/django/caches.py
```

## Single-instance constraint

```
$ ddx cache add memcached
A cache (redis) is already installed. Only one cache can be installed at a time.
```

## CLI commands

```
ddx cache add [NAME] [-v]
ddx cache remove [NAME] [-v]
ddx cache list
```

## Testing

```bash
ddx cache add redis
ddx cache list
ddx cache remove redis
```

Verify Docker Compose configuration:

```bash
cat .devcontainer/docker-compose.yaml
```

See [Testing](creating-an-installable.md#testing) for the CLI integration
test pattern and golden-file fixtures.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Cache Architecture](cache-architecture.md) — BaseCache details
- [Installable System](installable-system.md) — Shared infrastructure
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
