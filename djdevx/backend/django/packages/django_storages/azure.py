from .._base import BasePackage


class AzureStoragePackage(BasePackage):
    name = "django-storages Azure"
    packages = ["django-storages[azure]<2"]


_pkg = AzureStoragePackage(__file__)
app = _pkg.app
