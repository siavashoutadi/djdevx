from ._base import BasePackage


class DjangoAuditlogPackage(BasePackage):
    name = "django-auditlog"
    packages = ["django-auditlog<4"]


_pkg = DjangoAuditlogPackage(__file__)
app = _pkg.app
