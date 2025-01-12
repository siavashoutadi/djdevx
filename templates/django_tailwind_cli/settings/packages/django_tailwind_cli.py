from settings import BASE_DIR, INSTALLED_APPS


INSTALLED_APPS += [
    "django_tailwind_cli",
]

TAILWIND_CLI_SRC_CSS = BASE_DIR / "static" / "src" / "css" / "input.css"
