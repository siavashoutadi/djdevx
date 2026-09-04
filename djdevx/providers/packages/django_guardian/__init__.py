from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class DjangoGuardianPackage(BasePackage):
    name: str = "django-guardian"
    display_name: str = "Django Guardian"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-guardian")]

    def after_copy_templates(self, step=None) -> None:
        self._modify_user_model()

    def before_pixi_remove(self, step=None) -> None:
        self._revert_user_model()

    @property
    def _user_model_path(self):
        return self.structure.root / "users" / "models.py"

    def _modify_user_model(self) -> None:
        path = self._user_model_path
        if not path.exists():
            return
        content = path.read_text()

        if "from guardian.mixins import GuardianUserMixin" not in content:
            content = content.replace(
                "from django.contrib.auth.models import AbstractUser",
                "from django.contrib.auth.models import AbstractUser\nfrom guardian.mixins import GuardianUserMixin",
            )
        if "class User(AbstractUser):" in content:
            content = content.replace(
                "class User(AbstractUser):",
                "class User(AbstractUser, GuardianUserMixin):",
            )
        path.write_text(content)

    def _revert_user_model(self) -> None:
        path = self._user_model_path
        if not path.exists():
            return
        content = path.read_text()
        content = content.replace("\nfrom guardian.mixins import GuardianUserMixin", "")
        content = content.replace(
            "class User(AbstractUser, GuardianUserMixin):",
            "class User(AbstractUser):",
        )
        path.write_text(content)
