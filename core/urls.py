from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("login/", views.NovaLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path("equipo/", views.equipo, name="equipo"),
    path("password-reset/", views.NovaPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/enviado/", views.NovaPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password-reset/confirmar/<uidb64>/<token>/",
        views.NovaPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/completado/",
        views.NovaPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("2fa/activar/", views.activar_2fa, name="activar_2fa"),
    path("2fa/desactivar/", views.desactivar_2fa, name="desactivar_2fa"),
    path("2fa/verificar/", views.verificar_2fa, name="verificar_2fa"),
]
