from ._base import BasePackage


class DjangoAuditlogPackage(BasePackage):
    name = "django-auditlog"
    packages = ["django-auditlog"]


_pkg = DjangoAuditlogPackage(__file__)
app = _pkg.app
