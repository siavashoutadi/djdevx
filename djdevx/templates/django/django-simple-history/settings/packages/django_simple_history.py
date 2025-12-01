from settings import INSTALLED_APPS, MIDDLEWARE


INSTALLED_APPS += [
    "simple_history",
]

MIDDLEWARE += [
    "simple_history.middleware.HistoryRequestMiddleware",
]
