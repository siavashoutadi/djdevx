from settings import INSTALLED_APPS, MIDDLEWARE
from settings.django.auth import AUTHENTICATION_BACKENDS

from better_profanity import profanity


INSTALLED_APPS += [
    "authentication",
    "allauth",
    "allauth.account",
]

MIDDLEWARE += [
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS += [
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/auth/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "email2*", "username*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_MAX_EMAIL_ADDRESSES = 3
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_PREVENT_ENUMERATION = True
ACCOUNT_REAUTHENTICATION_REQUIRED = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Test Site] "
ACCOUNT_USERNAME_BLACKLIST = [str(word) for word in profanity.CENSOR_WORDSET]
ACCOUNT_FORMS = {
    "add_email": "authentication.forms.AuthAddEmailForm",
    "change_password": "authentication.forms.AuthChangePasswordForm",
    "login": "authentication.forms.AuthLoginForm",
    "reset_password": "authentication.forms.AuthResetPasswordForm",
    "reset_password_from_key": "authentication.forms.AuthResetPasswordKeyForm",
    "set_password": "authentication.forms.AuthSetPasswordForm",
    "signup": "authentication.forms.AuthSignupForm",
    "user_token": "authentication.forms.AuthUserTokenForm",
    "reauthenticate": "authentication.forms.AuthReauthenticateForm",
}
