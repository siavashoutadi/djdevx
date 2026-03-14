import shutil
import typer
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from .....utils.console.print import print_console

from .._base import BasePackage


class OidcProviderPackage(BasePackage):
    name = "django-allauth OIDC provider"
    packages = ["django-allauth[idp-oidc]"]
    env_vars = {}

    def install(self) -> None:
        """Install OIDC provider with account dependency check."""
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

        self.before_uv_install()
        self._uv_add_all()
        self.after_uv_install()
        self.before_copy_templates()
        self._copy_templates()
        self.after_copy_templates()
        self.env()

    def remove(self) -> None:
        """Remove OIDC provider configuration."""
        # Only remove configuration files, not django-allauth package (account depends on it)
        self._cleanup_files()
        self._remove_env_vars()
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
        self._remove_env_variable_from_file(
            self.pm.devcontainer_env_devcontainer_path, "IDP_OIDC_PRIVATE_KEY"
        )

    def env(self) -> None:
        """Generate RSA key for OIDC provider."""
        private_key_obj = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        private_key = private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        self.pm.add_env_variable(key="IDP_OIDC_PRIVATE_KEY", value=f"'{private_key}'")

    def _remove_env_variable_from_file(self, file_path: Path, key: str) -> None:
        """Remove environment variable from .env file."""
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(f"{key}="):
                i += 1
                while i < len(lines):
                    current_line = lines[i]
                    if "-----END" in current_line:
                        i += 1
                        if i < len(lines) and lines[i].strip() == "'":
                            i += 1
                        break
                    i += 1
            else:
                new_lines.append(line)
                i += 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)


_pkg = OidcProviderPackage(__file__)
app = _pkg.app
