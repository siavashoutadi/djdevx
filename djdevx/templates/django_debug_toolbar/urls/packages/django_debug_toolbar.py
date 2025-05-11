import sys
from settings.django.base import DEBUG

TESTING = "test" in sys.argv

if DEBUG and not TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = debug_toolbar_urls()
