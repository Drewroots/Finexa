from django import forms

from .models import Tercero


class TerceroForm(forms.ModelForm):
    class Meta:
        model = Tercero
        fields = [
            "tipo_documento",
            "numero_documento",
            "tipo",
            "razon_social",
            "email",
            "telefono",
            "direccion",
            "activo",
        ]
        widgets = {
            "tipo_documento": forms.Select(attrs={"class": "form-select"}),
            "numero_documento": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "razon_social": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
