from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DRFFlexFieldsPackage(BasePackage):
    name: str = "drf-flex-fields"
    display_name: str = "DRF Flex Fields"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("drf-flex-fields")]
