from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class WhitenoisePackage(BasePackage):
    name: str = "whitenoise"
    display_name: str = "Whitenoise"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("whitenoise<7")]
