"""Redis cache provider."""

import shutil

from .._base import BaseCache
from .._registry import register
from ....utils.devcontainer import ServiceConfig, VolumeConfig, DockerComposeManager
from ....utils.console.print import NestedStep
from ....utils.services import RedisService
from ....utils.types.pixi_types import PixiPackageSpec

REDIS_DOCKER_SERVICE: ServiceConfig = {
    "name": "cache",
    "image": "redis:7.4-alpine",
    "environment": {"REDIS_PASSWORD": "redis_password"},
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


@register
class RedisCache(BaseCache):
    name: str = "redis"
    display_name: str = "Redis"
    description: str = "Redis cache with django-redis integration"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="django-redis", kind="conda", pixi_feature="dev"),
        PixiPackageSpec(name="redis-server", kind="conda", pixi_feature="dev"),
    ]
    restore_on_remove: dict[str, str] = {
        "settings/django/sessions.py": "settings/django/sessions.py"
    }

    def after_pixi_install(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(REDIS_DOCKER_SERVICE, REDIS_VOLUMES, step=step)

    def after_pixi_remove(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(REDIS_DOCKER_SERVICE, REDIS_VOLUMES, step=step)
        self._wipe_dev_data()

    def _wipe_dev_data(self) -> None:
        service = RedisService(self.structure.root)
        try:
            if service.is_up():
                service.down()
        except OSError:
            pass
        shutil.rmtree(service.data_dir, ignore_errors=True)
