# https://docs.djangoproject.com/en/5.1/topics/settings/
# https://docs.djangoproject.com/en/5.1/ref/settings/

from settings import BASE_DIR


# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
SECRET_KEY: str = "django-insecure-sk%q2_j=huun7$4%+zcgz#=!@#r5#18-qc8%pz8um97nw-9mth"
DEBUG: bool = True
ALLOWED_HOSTS: list[str] = []
ROOT_URLCONF: str = "urls"
WSGI_APPLICATION: str = "applications.wsgi.application"
ASGI_APPLICATION: str = "applications.asgi.application"

INSTALLED_APPS: list[str] = [
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
