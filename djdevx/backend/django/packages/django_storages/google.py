from .._base import BasePackage


class GoogleStoragePackage(BasePackage):
    name = "django-storages Google Cloud Storage"
    packages = ["django-storages[google]"]


_pkg = GoogleStoragePackage(__file__)
app = _pkg.app
