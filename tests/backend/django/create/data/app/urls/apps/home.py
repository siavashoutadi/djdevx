from django.urls import include, path


urlpatterns = [
    path("home/", include("home.urls")),
]
