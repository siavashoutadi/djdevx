from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoSpAdminPackage(BasePackage):
    name: str = "django-sp-admin"
    display_name: str = "Django SP Admin"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec(
            "django-sp-admin @ https://github.com/siavashoutadi/django-sp-admin/releases/download/v0.1.1/django_sp_admin-0.1.0-py3-none-any.whl",
            kind="pypi",
        )
    ]
