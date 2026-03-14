import shutil

from .._base import BasePackage, InstallParam


class AllauthAccountPackage(BasePackage):
    name = "django-allauth account"
    packages = ["django-allauth"]

    install_params = [
        InstallParam(
            name="email_subject_prefix",
            help="Subject-line prefix for emails (e.g., '[example.com] - ')",
            prompt="Subject prefix for email messages",
        ),
        InstallParam(
            name="enable_login_by_code",
            type_=bool,
            default=True,
            help="Enable login by code",
            prompt="Enable login by code",
        ),
        InstallParam(
            name="is_profanity_for_username_enabled",
            type_=bool,
            default=True,
            help="Enable profanity filter for usernames",
            prompt="Enable profanity filter for username",
        ),
        InstallParam(
            name="account_url_prefix",
            default="auth",
            help="URL prefix for account URLs",
            prompt="URL prefix for account related URLs",
        ),
    ]

    def before_uv_install(self) -> None:
        """Conditionally add better-profanity before uv install."""
        if self._install_context.get("is_profanity_for_username_enabled", True):
            if "better-profanity" not in self.packages:
                self.packages = list(self.packages) + ["better-profanity"]

    def after_uv_remove(self) -> None:
        shutil.rmtree(self.pm.project_path / "authentication", ignore_errors=True)
        (self.pm.project_path / "static" / "css" / "vendor" / "auth.css").unlink(
            missing_ok=True
        )
        if self.pm.has_dependency("better-profanity"):
            self.uv.remove_package("better-profanity")


_pkg = AllauthAccountPackage(__file__)
app = _pkg.app
