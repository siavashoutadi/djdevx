from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoDebugToolbarPackage(BasePackage):
    name: str = "django-debug-toolbar"
    display_name: str = "Django Debug Toolbar"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-debug-toolbar", pixi_feature="dev")
    ]
