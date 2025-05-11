from settings.django.base import DEBUG
from django.urls import path, include


if DEBUG:
    urlpatterns = [
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework"))
    ]
