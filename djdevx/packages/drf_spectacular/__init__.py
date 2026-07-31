from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DRFSpectacularPackage(BasePackage):
    name: str = "drf-spectacular"
    display_name: str = "DRF Spectacular"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("drf-spectacular")]
