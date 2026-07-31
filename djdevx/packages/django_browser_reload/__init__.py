from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoBrowserReloadPackage(BasePackage):
    name: str = "django-browser-reload"
    display_name: str = "Django Browser Reload"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-browser-reload", pixi_feature="dev")
    ]
