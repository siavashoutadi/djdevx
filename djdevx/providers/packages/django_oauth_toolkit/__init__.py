from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoOAuthToolkitPackage(BasePackage):
    name: str = "django-oauth-toolkit"
    display_name: str = "Django OAuth Toolkit"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-oauth-toolkit")]
