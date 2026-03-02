from ._base import BasePackage


class DjangoImportExportPackage(BasePackage):
    name = "django-import-export"
    packages = ["django-import-export"]


_pkg = DjangoImportExportPackage(__file__)
app = _pkg.app
