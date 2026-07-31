from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoAuditlogPackage(BasePackage):
    name: str = "django-auditlog"
    display_name: str = "Django Auditlog"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-auditlog")]
