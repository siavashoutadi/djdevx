from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoCSPPackage(BasePackage):
    name: str = "django-csp"
    display_name: str = "Django CSP"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-csp")]
