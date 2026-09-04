from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoHealthCheckPackage(BasePackage):
    name: str = "django-health-check"
    display_name: str = "Django Health Check"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-health-check"),
        PixiPackageSpec("psutil", kind="pypi"),
    ]
