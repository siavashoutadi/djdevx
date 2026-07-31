import sys
from django.urls import path, include

TESTING = "test" in sys.argv

if not TESTING:
    urlpatterns = [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
else:
    urlpatterns = []
