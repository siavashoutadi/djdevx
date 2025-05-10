from django.urls import include, path


urlpatterns = [
    path("admin/defender/", include("defender.urls")),
]
