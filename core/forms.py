from django import forms
from django.contrib.auth.forms import UserCreationForm

from contabilidad.services import sembrar_plan_cuentas

from .models import Empresa, Usuario


class RegistroEmpresaForm(UserCreationForm):
    """Alta de una nueva empresa (tenant) junto con su primer usuario (dueño)."""

    empresa_nombre = forms.CharField(label="Nombre de la empresa", max_length=200)
    empresa_nit = forms.CharField(label="NIT", max_length=20)
    email = forms.EmailField(label="Correo electrónico")

    class Meta:
        model = Usuario
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        empresa = Empresa.objects.create(
            nombre=self.cleaned_data["empresa_nombre"],
            nit=self.cleaned_data["empresa_nit"],
            email=self.cleaned_data["email"],
        )
        sembrar_plan_cuentas(empresa)
        usuario.empresa = empresa
        usuario.email = self.cleaned_data["email"]
        usuario.rol = Usuario.ROL_DUENIO
        if commit:
            usuario.save()
        return usuario


class InvitarUsuarioForm(forms.ModelForm):
    """Permite al dueño de una empresa crear usuarios adicionales (contador, vendedor)."""

    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "rol"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, empresa, commit=True):
        usuario = super().save(commit=False)
        usuario.empresa = empresa
        usuario.set_password(self.cleaned_data["password1"])
        if commit:
            usuario.save()
        return usuario


class CodigoTOTPForm(forms.Form):
    codigo = forms.CharField(
        label="Código de 6 dígitos",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "inputmode": "numeric", "autocomplete": "one-time-code", "autofocus": True}
        ),
    )


class DesactivarTOTPForm(forms.Form):
    password = forms.CharField(label="Confirma tu contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}))
