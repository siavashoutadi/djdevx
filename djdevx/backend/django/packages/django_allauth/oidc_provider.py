import shutil
import typer

from .....utils.generators.rsa import generate_rsa_private_key
from .....utils.console.print import print_console

from .._base import BasePackage


class OidcProviderPackage(BasePackage):
    name = "django-allauth OIDC provider"
    packages = ["django-allauth[idp-oidc]"]

    # RSA private key is auto-generated; no manual input required.
    secret_generators = {
        "idp_oidc_private_key": generate_rsa_private_key,
    }

    def before_uv_install(self) -> None:
        """Ensure django-allauth account is installed before proceeding."""
        account_settings_path = (
            self.pm.packages_settings_path / "django_allauth_account.py"
        )
        if not account_settings_path.exists():
            print_console.error(
                "django-allauth account functionality is not configured. "
                "Please install it first."
            )
            print_console.info(
                "\n> ddx backend django packages django-allauth account install"
            )
            raise typer.Exit(code=1)

    def remove(self) -> None:
        """Remove OIDC provider configuration."""
        # Only remove configuration files, not django-allauth package (account depends on it)
        self._cleanup_files()
        shutil.rmtree(
            self.pm.project_path / "authentication" / "templates" / "idp" / "oidc",
            ignore_errors=True,
        )
        (
            self.pm.project_path
            / "authentication"
            / "management"
            / "commands"
            / "pkce_oauth.py"
        ).unlink(missing_ok=True)
        (
            self.pm.project_path
            / "authentication"
            / "management"
            / "commands"
            / "__init__.py"
        ).unlink(missing_ok=True)
        self.secret_manager.remove_secret("idp_oidc_private_key")


_pkg = OidcProviderPackage(__file__)
app = _pkg.app
