from settings.django.base import DEBUG

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
