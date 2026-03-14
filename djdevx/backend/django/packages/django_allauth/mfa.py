import shutil
import typer
from typing_extensions import Annotated

from .._base import BasePackage
from .....utils.console.print import print_console


class MfaPackage(BasePackage):
    name = "django-allauth MFA"
    packages = ["django-allauth[mfa]"]

    def install(
        self,
        enable_totp: Annotated[
            bool,
            typer.Option(
                help="Enable TOTP (Time-based One-Time Password)",
                prompt="Enable TOTP authentication",
            ),
        ] = True,
        enable_recovery_codes: Annotated[
            bool,
            typer.Option(
                help="Enable recovery codes",
                prompt="Enable recovery codes for account recovery",
            ),
        ] = True,
        enable_webauthn: Annotated[
            bool,
            typer.Option(
                help="Enable WebAuthn/passkeys",
                prompt="Enable WebAuthn/passkeys authentication",
            ),
        ] = False,
        enable_trust: Annotated[
            bool,
            typer.Option(
                help="Enable 'trust this browser' functionality",
                prompt="Enable 'trust this browser' functionality",
            ),
        ] = False,
        totp_issuer: Annotated[
            str,
            typer.Option(
                help="Issuer name for TOTP QR codes",
                prompt="Issuer name for TOTP QR codes",
            ),
        ] = "",
        totp_period: Annotated[int, typer.Option(min=15, max=300)] = 30,
        totp_digits: Annotated[int, typer.Option(min=6, max=8)] = 6,
        totp_tolerance: Annotated[int, typer.Option(min=0, max=5)] = 0,
        recovery_code_count: Annotated[int, typer.Option(min=5, max=20)] = 10,
        recovery_code_digits: Annotated[int, typer.Option(min=6, max=16)] = 8,
        passkey_login: Annotated[
            bool, typer.Option(prompt="Enable passkey login")
        ] = False,
        passkey_signup: Annotated[
            bool, typer.Option(prompt="Enable passkey signup")
        ] = False,
        webauthn_allow_insecure: Annotated[
            bool, typer.Option(prompt="Allow WebAuthn over insecure origins (dev only)")
        ] = False,
        trust_cookie_age_days: Annotated[int, typer.Option(min=1, max=365)] = 14,
    ) -> None:
        """Install django-allauth with MFA functionality."""
        account_settings_path = (
            self.pm.packages_settings_path / "django_allauth_account.py"
        )
        if not account_settings_path.exists():
            print_console.error(
                "django-allauth account is not installed. Please install it first."
            )
            print_console.info(
                "\n> ddx backend django packages django-allauth account install"
            )
            raise typer.Exit(code=1)

        self.before_uv_install()
        self._uv_add_all()
        self.after_uv_install()
        self.before_copy_templates()
        self._copy_templates(
            context={
                "enable_totp": enable_totp,
                "enable_recovery_codes": enable_recovery_codes,
                "enable_webauthn": enable_webauthn,
                "enable_trust": enable_trust,
                "totp_issuer": totp_issuer,
                "totp_period": totp_period,
                "totp_digits": totp_digits,
                "totp_tolerance": totp_tolerance,
                "recovery_code_count": recovery_code_count,
                "recovery_code_digits": recovery_code_digits,
                "passkey_login": passkey_login,
                "passkey_signup": passkey_signup,
                "webauthn_allow_insecure": webauthn_allow_insecure,
                "trust_cookie_age_days": trust_cookie_age_days,
            }
        )

        self.after_copy_templates()

    def remove(self) -> None:
        """Remove MFA configuration."""
        self.before_uv_remove()
        # Only remove configuration files, not django-allauth package (account depends on it)
        self._cleanup_files()
        self._remove_env_vars()
        shutil.rmtree(
            self.pm.project_path / "authentication" / "templates" / "mfa",
            ignore_errors=True,
        )
        (self.pm.project_path / "authentication" / "middleware.py").unlink(
            missing_ok=True
        )


_pkg = MfaPackage(__file__)
app = _pkg.app
