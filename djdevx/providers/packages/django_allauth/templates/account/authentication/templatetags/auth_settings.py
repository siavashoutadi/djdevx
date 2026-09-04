from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def login_by_code_enabled():
    """Check if login by code is enabled."""
    return getattr(settings, "ACCOUNT_LOGIN_BY_CODE_ENABLED", False)


@register.simple_tag
def passkey_login_enabled():
    """Check if passkey login is enabled."""
    supported_types = getattr(
        settings, "MFA_SUPPORTED_TYPES", ["recovery_codes", "totp"]
    )

    if "webauthn" not in supported_types:
        return False

    return getattr(settings, "MFA_PASSKEY_LOGIN_ENABLED", False)
