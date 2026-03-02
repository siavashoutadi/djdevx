from ._base import BasePackage


class DjangoOauthToolkitPackage(BasePackage):
    name = "django-oauth-toolkit"
    packages = ["django-oauth-toolkit"]


_pkg = DjangoOauthToolkitPackage(__file__)
app = _pkg.app
