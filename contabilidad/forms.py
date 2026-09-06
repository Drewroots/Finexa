from django import forms

from .models import CuentaContable


class AuxiliarCuentaForm(forms.ModelForm):
    """Alta/edición de una cuenta auxiliar (Art. 7 Decreto 2650): la empresa la
    define libremente a partir del 7º dígito. Tipo y naturaleza los fija la
    clase elegida, no se piden aquí."""

    class Meta:
        model = CuentaContable
        fields = ["codigo", "nombre", "cuenta_padre", "activa"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 11050501"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "cuenta_padre": forms.Select(attrs={"class": "form-select"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {"cuenta_padre": "Cuenta padre (opcional)"}

    def __init__(self, *args, empresa=None, tipo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cuenta_padre"].required = False
        if empresa is not None:
            qs = CuentaContable.objects.filter(empresa=empresa)
            if tipo:
                qs = qs.filter(tipo=tipo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            self.fields["cuenta_padre"].queryset = qs.order_by("codigo")


class CargarExtractoForm(forms.Form):
    archivo = forms.FileField(
        label="Extracto bancario (CSV)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".csv"}),
        help_text="Columnas: fecha (AAAA-MM-DD), descripcion, valor (positivo=consignación, negativo=retiro).",
    )


class ConciliarManualForm(forms.Form):
    movimiento_contable = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-select"}))

    def __init__(self, *args, opciones=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["movimiento_contable"].choices = opciones
