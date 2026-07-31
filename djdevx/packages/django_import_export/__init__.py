from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoImportExportPackage(BasePackage):
    name: str = "django-import-export"
    display_name: str = "Django Import Export"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-import-export")]
