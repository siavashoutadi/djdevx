from ._base import BasePackage


class WhitenoisePackage(BasePackage):
    name = "whitenoise"
    packages = ["whitenoise<7"]


_pkg = WhitenoisePackage(__file__)
app = _pkg.app
