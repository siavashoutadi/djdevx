from ._base import BasePackage, EnvVar


class DjangoDefenderPackage(BasePackage):
    name = "django-defender"
    packages = ["django-defender"]
    env_vars = [
        EnvVar(
            env_key="DEFENDER_REDIS_URL",
            value="redis://default:${REDIS_PASSWORD}@cache:6379/1",
        ),
    ]


_pkg = DjangoDefenderPackage(__file__)
app = _pkg.app
