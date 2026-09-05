from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "core"

urlpatterns = [
    path("login/", views.NovaLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path("equipo/", views.equipo, name="equipo"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="core/password_reset_form.html",
            email_template_name="core/password_reset_email.html",
            subject_template_name="core/password_reset_subject.txt",
            success_url=reverse_lazy("core:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/enviado/",
        auth_views.PasswordResetDoneView.as_view(template_name="core/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirmar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="core/password_reset_confirm.html",
            success_url=reverse_lazy("core:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/completado/",
        auth_views.PasswordResetCompleteView.as_view(template_name="core/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("2fa/activar/", views.activar_2fa, name="activar_2fa"),
    path("2fa/desactivar/", views.desactivar_2fa, name="desactivar_2fa"),
    path("2fa/verificar/", views.verificar_2fa, name="verificar_2fa"),
]
