"""Celery Beat scheduler provider.

Installs ``django-celery-beat`` (DB-backed periodic tasks), depends on the
Celery task-queue (auto-installed), switches the scheduler to the database
scheduler, and registers a devcontainer ``celery-beat`` compose service.
"""

from djdevx.core.console import NestedStep
from ....installable.models import TASK_QUEUE, InstallableRef
from ....utils.devcontainer import DockerComposeManager, ServiceConfig
from ....utils.types.pixi_types import PixiPackageSpec
from .._base import BaseScheduler
from .._registry import register

CELERY_BEAT_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-beat",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "celery-worker", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery beat --loglevel=info",
}


@register
class CeleryBeatScheduler(BaseScheduler):
    name: str = "celery-beat"
    display_name: str = "Celery Beat"
    description: str = "Celery Beat — database-backed periodic task scheduler"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(name="django-celery-beat", kind="pypi"),
    ]
    needs: list[InstallableRef] = [
        InstallableRef("celery", TASK_QUEUE),
    ]

    def after_pixi_install(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(CELERY_BEAT_DOCKER_SERVICE, [], step=step)

    def after_pixi_remove(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(CELERY_BEAT_DOCKER_SERVICE, [], step=step)
        self._stop_daemon()

    def _stop_daemon(self) -> None:
        from ....services import CeleryBeatService

        service = CeleryBeatService(self.structure.root)
        try:
            if service.is_up():
                service.down()
        except OSError:
            pass
