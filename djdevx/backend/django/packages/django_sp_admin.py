from ._base import BasePackage


class DjangoSpAdminPackage(BasePackage):
    name = "django-sp-admin"
    packages = [
        "https://github.com/siavashoutadi/django-sp-admin/releases/download/v0.1.1/django_sp_admin-0.1.0-py3-none-any.whl"
    ]


_pkg = DjangoSpAdminPackage(__file__)
app = _pkg.app
