from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class HeroiconsPackage(BasePackage):
    name: str = "heroicons"
    display_name: str = "Heroicons"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("heroicons")]
