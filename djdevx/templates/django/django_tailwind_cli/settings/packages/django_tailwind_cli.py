from settings import BASE_DIR
from settings.django.base import INSTALLED_APPS

INSTALLED_APPS += [
    "django_tailwind_cli",
]

TAILWIND_CLI_SRC_CSS = BASE_DIR / "tailwind" / "src" / "css" / "input.css"
TAILWIND_CLI_DIST_CSS = "css/tailwind.min.css"
