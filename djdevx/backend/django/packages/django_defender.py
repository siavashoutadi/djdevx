from ._base import BasePackage


class DjangoDefenderPackage(BasePackage):
    name = "django-defender"
    packages = ["django-defender"]
    env_vars = {
        "DEFENDER_REDIS_URL": "redis://default:${REDIS_PASSWORD}@cache:6379/1",
    }


_pkg = DjangoDefenderPackage(__file__)
app = _pkg.app
