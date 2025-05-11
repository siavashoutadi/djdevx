from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path(settings.HEALTH_CHECK_URL, include("health_check.urls")),
]
