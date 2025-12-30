from settings.django.base import MIDDLEWARE
from typing import Dict, List

permission_policy_middleware = "django_permissions_policy.PermissionsPolicyMiddleware"

if permission_policy_middleware not in MIDDLEWARE:
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(security_index + 1, permission_policy_middleware)


PERMISSIONS_POLICY: Dict[str, List[str]] = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}
