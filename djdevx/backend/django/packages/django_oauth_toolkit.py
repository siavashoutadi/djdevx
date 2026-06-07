from ._base import BasePackage


class DjangoOauthToolkitPackage(BasePackage):
    name = "django-oauth-toolkit"
    packages = ["django-oauth-toolkit<4"]


_pkg = DjangoOauthToolkitPackage(__file__)
app = _pkg.app
