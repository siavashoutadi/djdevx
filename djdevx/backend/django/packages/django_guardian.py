from ._base import BasePackage


class DjangoGuardianPackage(BasePackage):
    name = "django-guardian"
    packages = ["django-guardian"]

    def after_copy_templates(self) -> None:
        self._add_guardian_mixin()

    def before_uv_remove(self) -> None:
        self._remove_guardian_mixin()

    def _add_guardian_mixin(self) -> None:
        """Add GuardianUserMixin to User model."""
        project_dir = self.pm.project_path
        user_model_file = project_dir / "users" / "models.py"

        if user_model_file.exists():
            content = user_model_file.read_text()
            if "GuardianUserMixin" not in content:
                updated_content = content.replace(
                    "from django.contrib.auth.models import AbstractUser",
                    "from django.contrib.auth.models import AbstractUser\nfrom guardian.mixins import GuardianUserMixin",
                ).replace(
                    "class User(AbstractUser):",
                    "class User(AbstractUser, GuardianUserMixin):",
                )
                user_model_file.write_text(updated_content)

    def _remove_guardian_mixin(self) -> None:
        """Remove GuardianUserMixin from User model."""
        project_dir = self.pm.project_path
        user_model_file = project_dir / "users" / "models.py"

        if user_model_file.exists():
            content = user_model_file.read_text()
            if "GuardianUserMixin" in content:
                updated_content = (
                    "\n".join(
                        line
                        for line in content.splitlines()
                        if "from guardian.mixins import GuardianUserMixin" not in line
                    ).replace(
                        "class User(AbstractUser, GuardianUserMixin):",
                        "class User(AbstractUser):",
                    )
                    + "\n"
                )
                user_model_file.write_text(updated_content)


_pkg = DjangoGuardianPackage(__file__)
app = _pkg.app
