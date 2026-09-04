from ....utils.installable.types import (
    CACHE,
    DATABASE,
    InstallableRef,
)
from ....utils.tracking import ProjectTracking
from ....utils.types.pixi_types import PixiPackageSpec
from ....utils.devcontainer import DockerComposeManager, ServiceConfig
from ....utils.console.print import NestedStep
from .._base import BaseFeature
from .._registry import register

OTLP_DOCKER_SERVICE: ServiceConfig = {
    "name": "otlp",
    "image": "otel/opentelemetry-collector-contrib:0.159.0",
    "command": "--config=/etc/otelcol-contrib/config.yaml",
    "volumes": ["./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml:ro"],
    "networks": ["devcontainer"],
}

OPENOBSERVE_ROOT_USER_EMAIL = "admin@example.com"
OPENOBSERVE_ROOT_USER_PASSWORD = "ZoAdmin123!"

OPENOBSERVE_DOCKER_SERVICE: ServiceConfig = {
    "name": "openobserve",
    "image": "public.ecr.aws/zinclabs/openobserve:v0.92.2",
    "environment": {
        "ZO_ROOT_USER_EMAIL": OPENOBSERVE_ROOT_USER_EMAIL,
        "ZO_ROOT_USER_PASSWORD": OPENOBSERVE_ROOT_USER_PASSWORD,
    },
    "ports": ["5080"],
    "networks": ["devcontainer"],
}


@register
class OtelFeature(BaseFeature):
    name: str = "otel"
    display_name: str = "OpenTelemetry"
    description: str = "OpenTelemetry tracing for Django"

    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("opentelemetry-sdk==1.44.0", kind="pypi"),
        PixiPackageSpec("opentelemetry-instrumentation-django==0.65b0", kind="pypi"),
        PixiPackageSpec("opentelemetry-instrumentation-logging==0.65b0", kind="pypi"),
        PixiPackageSpec("opentelemetry-exporter-otlp-proto-http==1.44.0", kind="pypi"),
    ]

    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        InstallableRef("postgres", DATABASE): [
            PixiPackageSpec(
                "opentelemetry-instrumentation-psycopg2==0.65b0", kind="pypi"
            )
        ],
        InstallableRef("redis", CACHE): [
            PixiPackageSpec("opentelemetry-instrumentation-redis==0.65b0", kind="pypi")
        ],
    }

    def after_pixi_install(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(OTLP_DOCKER_SERVICE, [], step=step)
        compose.add_service(OPENOBSERVE_DOCKER_SERVICE, [], step=step)

    def before_copy_templates(self, step: NestedStep | None = None) -> None:
        tracking = ProjectTracking(self.structure.root)
        project_name = (
            tracking.get_config().get("project_name") or self.structure.root.name
        )
        self._install_context.setdefault("project_name", project_name)

    def after_pixi_remove(self, step: NestedStep | None = None) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(OTLP_DOCKER_SERVICE, [], step=step)
        compose.remove_service(OPENOBSERVE_DOCKER_SERVICE, [], step=step)
