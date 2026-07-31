# Cache Architecture

Caches manage cache providers (Redis) with Docker Compose integration. Only
**one** cache can be installed at a time — same constraint as databases.

## BaseCache

`BaseCache` (`djdevx/cache/_base.py`) extends `Installable` with
`section: str = "cache"`. It adds no additional attributes — all behavior
comes from `Installable`.

### Single-Instance Constraint

```
$ ddx cache add memcached
A cache (redis) is already installed. Only one cache can be installed at a time.
```

### Hook-Based Pattern

Caches use lifecycle hooks for Docker Compose configuration — they do **not**
override `install()` and `remove()` directly:

```python
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

### Docker Service Configs

Define Docker Compose service configurations as module-level constants:

```python
from ...utils.devcontainer import ServiceConfig, VolumeConfig

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
```

Use `DockerComposeManager` to add/remove services in the appropriate hooks.

### Concrete Example

The Redis provider (`djdevx/cache/redis/__init__.py`) demonstrates the
pattern:

- Defines Docker service config with password authentication
- Uses `after_pixi_install()` to add the service
- Uses `restore_on_remove` to restore the default sessions template
- Uses `after_pixi_remove()` to remove the service

## CLI Commands

```
ddx cache add [NAME] [-v]       # Install a cache
ddx cache remove [NAME] [-v]    # Remove a cache
ddx cache list                   # List all caches
```

The `add` command uses `prompts.select()` (single-choice).

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Cache](adding-a-cache.md) — Step-by-step guide
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
