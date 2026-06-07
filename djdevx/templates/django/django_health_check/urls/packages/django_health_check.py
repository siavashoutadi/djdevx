from django.conf import settings
from django.urls import path
from health_check.views import HealthCheckView

urlpatterns = [
    path(
        settings.HEALTH_CHECK_URL,
        HealthCheckView.as_view(checks=settings.HEALTH_CHECKS),
    ),
]
