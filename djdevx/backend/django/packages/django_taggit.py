from ._base import BasePackage


class DjangoTaggitPackage(BasePackage):
    name = "django-taggit"
    packages = ["django-taggit"]


_pkg = DjangoTaggitPackage(__file__)
app = _pkg.app
