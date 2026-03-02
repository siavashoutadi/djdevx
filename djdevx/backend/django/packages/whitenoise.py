from ._base import BasePackage


class WhitenoisePackage(BasePackage):
    name = "whitenoise"
    packages = ["whitenoise"]


_pkg = WhitenoisePackage(__file__)
app = _pkg.app
