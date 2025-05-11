from settings import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS += [
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]
