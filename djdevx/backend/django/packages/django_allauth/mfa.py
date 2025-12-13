import typer
from pathlib import Path
from typing_extensions import Annotated
import shutil

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    enable_totp: Annotated[
        bool,
        typer.Option(
            help="Enable TOTP authentication",
            prompt="Enable TOTP (Time-based One-Time Password) authentication",
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
            help="Enable WebAuthn/passkeys authentication",
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
            prompt="Please enter the issuer name for TOTP QR codes (e.g., 'My App')",
        ),
    ] = "",
    totp_period: Annotated[
        int,
        typer.Option(
            help="TOTP token validity period in seconds",
            min=15,
            max=300,
        ),
    ] = 30,
    totp_digits: Annotated[
        int,
        typer.Option(
            help="Number of digits in TOTP tokens",
            min=6,
            max=8,
        ),
    ] = 6,
    totp_tolerance: Annotated[
        int,
        typer.Option(
            help="TOTP time tolerance (number of periods to allow)",
            min=0,
            max=5,
        ),
    ] = 0,
    recovery_code_count: Annotated[
        int,
        typer.Option(
            help="Number of recovery codes to generate",
            min=5,
            max=20,
        ),
    ] = 10,
    recovery_code_digits: Annotated[
        int,
        typer.Option(
            help="Number of digits in each recovery code",
            min=6,
            max=16,
        ),
    ] = 8,
    passkey_login: Annotated[
        bool,
        typer.Option(
            help="Enable passkey login",
            prompt="Enable passkey login",
        ),
    ] = False,
    passkey_signup: Annotated[
        bool,
        typer.Option(
            help="Enable passkey signup",
            prompt="Enable passkey signup",
        ),
    ] = False,
    webauthn_allow_insecure: Annotated[
        bool,
        typer.Option(
            help="Allow WebAuthn over insecure origins (for development)",
            prompt="Allow WebAuthn over insecure origins (for development)",
        ),
    ] = False,
    trust_cookie_age_days: Annotated[
        int,
        typer.Option(
            help="Trust cookie validity period in days",
            min=1,
            max=365,
            prompt="Trust cookie validity period in days",
        ),
    ] = 14,
):
    """
    Install django-allauth package with MFA functionality
    """
    pm = DjangoProjectManager()

    console.step("Checking if django-allauth account is installed ...")
    if not pm.has_dependency("django-allauth"):
        console.error(
            "'django-allauth' package is not installed. Please install django-allauth account functionality first."
        )
        console.info("\n> ddx backend django packages django-allauth account install")
        raise typer.Exit(1)

    # Check if account settings exist
    account_settings_path = Path.joinpath(
        pm.packages_settings_path, "django_allauth_account.py"
    )
    if not account_settings_path.exists():
        console.error(
            "django-allauth account functionality is not configured. Please install it first."
        )
        console.info("\n> ddx backend django packages django-allauth account install")
        raise typer.Exit(1)

    console.step("Installing django-allauth package with MFA functionality ...")

    uv = UvRunner()
    uv.add_package("django-allauth[mfa]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_allauth"
        / "mfa"
    )

    pm.copy_templates(
        source_dir=source_dir,
        template_context={
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
        },
    )

    console.success("django-allauth with MFA functionality is installed successfully.")


@app.command()
def remove():
    """
    Remove django-allauth MFA configuration

    Note: This removes MFA configuration but keeps the django-allauth[mfa]
    package installed with its dependencies. To completely remove django-allauth,
    use the account remove command.
    """
    pm = DjangoProjectManager()

    console.step("Removing django-allauth MFA configuration ...")

    # Remove MFA settings file
    mfa_settings_path = Path.joinpath(
        pm.packages_settings_path, "django_allauth_mfa.py"
    )
    mfa_settings_path.unlink(missing_ok=True)

    middleware_path = Path.joinpath(pm.project_path, "authentication", "middleware.py")

    middleware_path.unlink(missing_ok=True)

    templates_dir = Path.joinpath(pm.project_path, "authentication", "templates", "mfa")

    shutil.rmtree(templates_dir, ignore_errors=True)

    console.success("django-allauth MFA configuration is removed successfully.")
    console.info(
        "Note: django-allauth[mfa] package remains installed. Use 'ddx backend django packages django-allauth account remove' to remove the entire package."
    )
