from .._base import BasePackage


class GoogleStoragePackage(BasePackage):
    name = "django-storages Google Cloud Storage"
    packages = ["django-storages[google]<2"]


_pkg = GoogleStoragePackage(__file__)
app = _pkg.app
