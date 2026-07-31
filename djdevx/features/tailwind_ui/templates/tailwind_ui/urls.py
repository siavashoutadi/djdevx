from django.urls import path
from .views import home


urlpatterns = [
    path("", home, name="tailwind_ui_home"),
]
