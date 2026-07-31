from django.urls import path
from .views import pwa_manifest, pwa_service_worker


urlpatterns = [
    path("sw.js", pwa_service_worker, name="service-worker"),
    path("manifest.json", pwa_manifest, name="manifest"),
]
