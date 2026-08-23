from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import InvitarUsuarioForm, RegistroEmpresaForm
from .models import Usuario


class NovaLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True


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
