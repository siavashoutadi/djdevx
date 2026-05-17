"""Redis cache management."""

from pathlib import Path
import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.devcontainer import ServiceConfig, VolumeConfig

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
    pm.copy_templates(source_dir=source_dir, template_context=context)

    pm.add_service_to_docker_compose(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)

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

    for key in REDIS_ENV_VARIABLES:
        pm.remove_env_variable(key, pm.devcontainer_env_devcontainer_path)

    pm.remove_env_file("redis")
    pm.remove_service_from_docker_compose(REDIS_DOCKER_SERVICE, REDIS_VOLUMES)

    print_console.success("Redis cache removed successfully!")
