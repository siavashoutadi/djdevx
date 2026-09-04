from settings.django.base import INSTALLED_APPS
from settings.packages.djangorestframework import REST_FRAMEWORK

INSTALLED_APPS += ["drf_spectacular", "drf_spectacular_sidecar"]

REST_FRAMEWORK.update(
    {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }
)

SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
