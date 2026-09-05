import pyotp

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import CodigoTOTPForm, DesactivarTOTPForm, InvitarUsuarioForm, RegistroEmpresaForm
from .models import Usuario

SESSION_KEY_PRE_2FA_USER = "pre_2fa_user_id"
SESSION_KEY_PENDING_TOTP_SECRET = "pending_totp_secret"


class NovaLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        usuario = form.get_user()
        if usuario.totp_habilitado:
            self.request.session[SESSION_KEY_PRE_2FA_USER] = usuario.pk
            return redirect("core:verificar_2fa")
        return super().form_valid(form)


def registro(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        form = RegistroEmpresaForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("dashboard:index")
    else:
        form = RegistroEmpresaForm()

    return render(request, "core/registro.html", {"form": form})


@login_required
def equipo(request):
    """Lista y alta de usuarios (contador, vendedor) dentro de la empresa del dueño."""
    if not request.user.es_duenio:
        return redirect("dashboard:index")

    empresa = request.empresa
    if request.method == "POST":
        form = InvitarUsuarioForm(request.POST)
        if form.is_valid():
            form.save(empresa=empresa)
            return redirect("core:equipo")
    else:
        form = InvitarUsuarioForm()

    usuarios = Usuario.objects.filter(empresa=empresa).order_by("username")
    return render(request, "core/equipo.html", {"form": form, "usuarios": usuarios})


def verificar_2fa(request):
    """Segundo paso del login cuando el usuario tiene 2FA activado."""
    user_id = request.session.get(SESSION_KEY_PRE_2FA_USER)
    if not user_id:
        return redirect("core:login")
    usuario = get_object_or_404(Usuario, pk=user_id)

    if request.method == "POST":
        form = CodigoTOTPForm(request.POST)
        if form.is_valid():
            totp = pyotp.TOTP(usuario.totp_secret)
            if totp.verify(form.cleaned_data["codigo"], valid_window=1):
                del request.session[SESSION_KEY_PRE_2FA_USER]
                login(request, usuario)
                return redirect("dashboard:index")
            form.add_error("codigo", "Código inválido o expirado.")
    else:
        form = CodigoTOTPForm()

    return render(request, "core/verificar_2fa.html", {"form": form})


@login_required
def activar_2fa(request):
    """Configura la autenticacion en dos pasos (TOTP) para el usuario actual."""
    usuario = request.user
    if usuario.totp_habilitado:
        return render(request, "core/gestionar_2fa.html", {"desactivar_form": DesactivarTOTPForm()})

    secreto = request.session.get(SESSION_KEY_PENDING_TOTP_SECRET)
    if not secreto:
        secreto = pyotp.random_base32()
        request.session[SESSION_KEY_PENDING_TOTP_SECRET] = secreto

    if request.method == "POST":
        form = CodigoTOTPForm(request.POST)
        if form.is_valid():
            totp = pyotp.TOTP(secreto)
            if totp.verify(form.cleaned_data["codigo"], valid_window=1):
                usuario.totp_secret = secreto
                usuario.totp_habilitado = True
                usuario.save(update_fields=["totp_secret", "totp_habilitado"])
                del request.session[SESSION_KEY_PENDING_TOTP_SECRET]
                messages.success(request, "Autenticación en dos pasos activada correctamente.")
                return redirect("core:activar_2fa")
            form.add_error("codigo", "Código inválido. Verifica la hora de tu dispositivo e intenta de nuevo.")
    else:
        form = CodigoTOTPForm()

    otpauth_uri = pyotp.TOTP(secreto).provisioning_uri(name=usuario.username, issuer_name="NovaERP")
    return render(
        request,
        "core/activar_2fa.html",
        {"form": form, "secreto": secreto, "otpauth_uri": otpauth_uri},
    )


@login_required
def desactivar_2fa(request):
    usuario = request.user
    if request.method == "POST":
        form = DesactivarTOTPForm(request.POST)
        if form.is_valid() and usuario.check_password(form.cleaned_data["password"]):
            usuario.totp_secret = ""
            usuario.totp_habilitado = False
            usuario.save(update_fields=["totp_secret", "totp_habilitado"])
            messages.success(request, "Autenticación en dos pasos desactivada.")
            return redirect("core:activar_2fa")
        messages.error(request, "Contraseña incorrecta.")
    return redirect("core:activar_2fa")
