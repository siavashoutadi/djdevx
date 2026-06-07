from .._base import BasePackage


class S3Package(BasePackage):
    name = "django-storages S3"
    packages = ["django-storages[s3]"]


_pkg = S3Package(__file__)
app = _pkg.app
