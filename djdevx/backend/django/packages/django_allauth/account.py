import shutil
import typer
from typing_extensions import Annotated

from .._base import BasePackage


class AllauthAccountPackage(BasePackage):
    name = "django-allauth account"
    packages = ["django-allauth"]

    def install(
        self,
        email_subject_prefix: Annotated[
            str,
            typer.Option(
                help="Subject-line prefix for emails (e.g., '[example.com] - ')",
                prompt="Subject prefix for email messages",
            ),
        ] = "",
        enable_login_by_code: Annotated[
            bool,
            typer.Option(
                help="Enable login by code",
                prompt="Enable login by code",
            ),
        ] = True,
        is_profanity_for_username_enabled: Annotated[
            bool,
            typer.Option(
                help="Enable profanity filter for usernames",
                prompt="Enable profanity filter for username",
            ),
        ] = True,
        account_url_prefix: Annotated[
            str,
            typer.Option(
                help="URL prefix for account URLs",
                prompt="URL prefix for account related URLs",
            ),
        ] = "auth",
    ) -> None:
        """Install django-allauth with account functionality."""

        if is_profanity_for_username_enabled:
            self.packages.append("better-profanity")

        self._uv_add_all()
        self._copy_templates(
            context={
                "email_subject_prefix": email_subject_prefix,
                "enable_login_by_code": enable_login_by_code,
                "is_profanity_for_username_enabled": is_profanity_for_username_enabled,
                "account_url_prefix": account_url_prefix,
            }
        )

    def remove(self) -> None:
        """Remove django-allauth account and related dependencies."""
        super().remove()
        shutil.rmtree(self.pm.project_path / "authentication", ignore_errors=True)
        (self.pm.project_path / "static" / "css" / "vendor" / "auth.css").unlink(
            missing_ok=True
        )

        if self.pm.has_dependency("better-profanity"):
            self.uv.remove_package("better-profanity")


_pkg = AllauthAccountPackage(__file__)
app = _pkg.app
