"""Redis cache management."""

from pathlib import Path
import typer

from djdevx.utils.templates.manager import TemplateManager

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.devcontainer import ServiceConfig, VolumeConfig
from ....utils.djdevx_config.backend import CacheTracker

REDIS_ENV_VARIABLES = {
    "REDIS_PASSWORD": "redis_password",
    "CACHE_LOCATION": "redis://default@cache:6379/1",
}
REDIS_DEPENDENCY = "django-redis"
REDIS_DOCKER_SERVICE: ServiceConfig = {
    "name": "cache",
    "image": "redis:7.4-alpine",
    "env_file": ["./.env/redis"],
    "command": "/bin/sh -c 'redis-server --appendonly yes --requirepass $${REDIS_PASSWORD}'",
    "volumes": ["cache-data:/data"],
    "networks": ["devcontainer"],
}

REDIS_VOLUMES: list[VolumeConfig] = [
    {
        "name": "cache-data",
        "driver": "local",
    }
]

app = typer.Typer(no_args_is_help=True)


@app.command()
def install() -> None:
    """Install Redis cache."""
    pm = DjangoProjectManager()

    pm.add_dependency(REDIS_DEPENDENCY)

    for key, value in REDIS_ENV_VARIABLES.items():
        pm.add_env_variable(key, value, pm.devcontainer_env_devcontainer_path)

    current_dir = Path(__file__).resolve().parent

    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "cache" / "redis"
    )

    context = {key.lower(): value for key, value in REDIS_ENV_VARIABLES.items()}
    context.update({"backend_root": str(pm.project_path)})

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir, dest_dir=pm.project_path.parent, template_context=context
    )

    pm.add_service_to_docker_compose(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)

    tracker = CacheTracker()
    tracker.write_cache_config("redis", "redis")
    tracker.write_env_entries(
        "redis",
        {
            "REDIS_PASSWORD": {"type": "secret"},
            "CACHE_LOCATION": {
                "type": "user_input",
                "value": "redis://default@cache:6379/1",
            },
        },
    )

    print_console.success("Redis cache installed successfully!")


@app.command()
def remove() -> None:
    """Remove Redis cache."""
    pm = DjangoProjectManager()

    pm.remove_dependency(REDIS_DEPENDENCY)

    cache_file = pm.django_settings_path / "caches.py"
    if cache_file.exists():
        cache_file.unlink()
        print_console.step("Removed cache settings")

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
        / "sessions.py"
    )

    pm.copy_template(source_file=source_dir, dest_dir=pm.django_settings_path)

    for key in REDIS_ENV_VARIABLES:
        pm.remove_env_variable(key, pm.devcontainer_env_devcontainer_path)

    pm.remove_env_file("redis")
    pm.remove_service_from_docker_compose(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)

    CacheTracker().remove_cache_config("redis")

    print_console.success("Redis cache removed successfully!")
