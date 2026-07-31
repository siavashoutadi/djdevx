from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DRFNestedRoutersPackage(BasePackage):
    name: str = "drf-nested-routers"
    display_name: str = "DRF Nested Routers"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("drf-nested-routers", kind="pypi")
    ]
