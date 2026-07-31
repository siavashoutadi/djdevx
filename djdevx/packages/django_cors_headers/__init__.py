from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoCorsHeadersPackage(BasePackage):
    name: str = "django-cors-headers"
    display_name: str = "Django CORS Headers"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-cors-headers")]
