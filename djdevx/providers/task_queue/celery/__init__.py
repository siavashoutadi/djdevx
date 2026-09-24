"""Celery task-queue provider.

Installs Celery, wires the Django broker/result settings, auto-installs the
Redis cache as the broker (``needs``), and registers a devcontainer
``celery-worker`` compose service. On a plain machine the worker runs as a
pixi-native daemon via ``ddx dev start`` (see
:mod:`djdevx.services.celery`).
"""

from djdevx.core.console import NestedStep
from ....installable.models import CACHE, InstallableRef
from ....utils.devcontainer import DockerComposeManager, ServiceConfig
from ....utils.tracking import ProjectTracking
from ....utils.types.pixi_types import PixiPackageSpec
from .._base import BaseTaskQueue
from .._registry import register

CELERY_WORKER_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-worker",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery worker --loglevel=info",
}


@register
class CeleryTaskQueue(BaseTaskQueue):
    name: str = "celery"
    display_name: str = "Celery"
    description: str = "Celery distributed task queue"
    # The Redis client ships with the auto-installed Redis cache
    # (django-redis -> conda redis), so celery only needs the app package.
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="celery", kind="pypi"),
    ]
    needs: list[InstallableRef] = [
        InstallableRef("redis", CACHE),
    ]

    def before_copy_templates(self, step: NestedStep | None = None) -> None:
        tracking = ProjectTracking(self.structure.root)
        project_name = (
            tracking.get_config().get("project_name") or self.structure.root.name
        )
        self._install_context.setdefault("project_name", project_name)

    def after_pixi_install(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(CELERY_WORKER_DOCKER_SERVICE, [], step=step)

    def after_pixi_remove(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(CELERY_WORKER_DOCKER_SERVICE, [], step=step)
        self._stop_daemon()

    def _stop_daemon(self) -> None:
        from ....services import CeleryWorkerService

        service = CeleryWorkerService(self.structure.root)
        try:
            if service.is_up():
                service.down()
        except OSError:
            pass
