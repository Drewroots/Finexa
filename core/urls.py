from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("login/", views.NovaLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path("equipo/", views.equipo, name="equipo"),
]
