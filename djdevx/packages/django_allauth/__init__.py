"""AllauthPackage — django-allauth with account (required), mfa, and oidc-provider."""

from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ...utils.installable.types import InstallParam, Variant
from .._registry import register
from ...utils.generators import generate_rsa_private_key


@register
class AllauthPackage(BasePackage):
    name: str = "django-allauth"
    display_name: str = "Django Allauth"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-allauth<66")]
    exclusive_variants: bool = False
    variants: dict[str, Variant] = {
        "account": Variant(
            name="account",
            display_name="Account",
            required=True,
            template_path="account",
            install_params=[
                InstallParam(
                    name="email_subject_prefix",
                    help="Subject-line prefix for emails (e.g. '[example.com] - ')",
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
                    name="account_url_prefix",
                    default="auth",
                    help="URL prefix for account URLs",
                    prompt="URL prefix for account related URLs",
                ),
            ],
        ),
        "mfa": Variant(
            name="mfa",
            display_name="MFA (Multi-Factor Authentication)",
            template_path="mfa",
            install_params=[
                InstallParam(name="enable_totp", type_=bool, default=True),
                InstallParam(name="enable_recovery_codes", type_=bool, default=True),
                InstallParam(name="enable_webauthn", type_=bool, default=False),
                InstallParam(name="enable_trust", type_=bool, default=False),
                InstallParam(name="totp_issuer", default=""),
                InstallParam(name="totp_period", type_=int, default=30),
                InstallParam(name="totp_digits", type_=int, default=6),
                InstallParam(name="totp_tolerance", type_=int, default=0),
                InstallParam(name="recovery_code_count", type_=int, default=10),
                InstallParam(name="recovery_code_digits", type_=int, default=8),
                InstallParam(name="passkey_login", type_=bool, default=False),
                InstallParam(name="passkey_signup", type_=bool, default=False),
                InstallParam(name="webauthn_allow_insecure", type_=bool, default=False),
                InstallParam(name="trust_cookie_age_days", type_=int, default=14),
            ],
        ),
        "oidc-provider": Variant(
            name="oidc-provider",
            display_name="OIDC Provider",
            template_path="oidc_provider",
            secret_generators={
                "idp_oidc_private_key": generate_rsa_private_key,
            },
        ),
    }

    def after_pixi_remove(self) -> None:
        import shutil

        shutil.rmtree(self.structure.root / "authentication", ignore_errors=True)
        (self.structure.root / "static" / "css" / "vendor" / "auth.css").unlink(
            missing_ok=True
        )
        for js_file in (
            "allauth-toasts.js",
            "allauth-theme.js",
            "email-remove.js",
        ):
            (self.structure.root / "static" / "js" / js_file).unlink(missing_ok=True)
