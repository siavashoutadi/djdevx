from settings.django.base import DEBUG
from django.urls import path, include


if DEBUG:
    urlpatterns = [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
