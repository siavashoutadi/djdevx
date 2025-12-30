from settings.django.base import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "allauth.mfa",
]

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
    "authentication.middleware.MFARequiredMiddleware",
)

# MFA Configuration
MFA_SUPPORTED_TYPES = [
    "recovery_codes",
    "totp",
]

MFA_TOTP_ISSUER = "Test App"
MFA_TOTP_PERIOD = 30
MFA_TOTP_DIGITS = 6
MFA_TOTP_TOLERANCE = 0

MFA_RECOVERY_CODE_COUNT = 10
MFA_RECOVERY_CODE_DIGITS = 8

MFA_ALLOW_UNVERIFIED_EMAIL = False
