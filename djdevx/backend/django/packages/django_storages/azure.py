from .._base import BasePackage


class AzureStoragePackage(BasePackage):
    name = "django-storages Azure"
    packages = ["django-storages[azure]"]


_pkg = AzureStoragePackage(__file__)
app = _pkg.app
