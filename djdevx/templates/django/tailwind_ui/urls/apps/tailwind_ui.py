from settings.django.base import DEBUG
from django.urls import include, path


if DEBUG:
    urlpatterns = [
        path("twui/", include("tailwind_ui.urls")),
    ]
