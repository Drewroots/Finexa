from decimal import Decimal

from django import forms

from .models import Empleado


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["nombre_completo", "numero_documento", "cargo", "salario_base", "fecha_ingreso", "activo"]
        widgets = {
            "nombre_completo": forms.TextInput(attrs={"class": "form-control"}),
            "numero_documento": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "salario_base": forms.NumberInput(attrs={"class": "form-control"}),
            "fecha_ingreso": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class LiquidarNominaForm(forms.Form):
    CUENTA_CHOICES = [("1105", "Caja"), ("1110", "Bancos")]
    MES_CHOICES = [(i, i) for i in range(1, 13)]

    anio = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    mes = forms.ChoiceField(choices=MES_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    dias_trabajados = forms.IntegerField(
        initial=30, min_value=1, max_value=30, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    otros_devengados = forms.DecimalField(
        initial=Decimal("0"), required=False, max_digits=14, decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text="Bonificaciones, comisiones u otros pagos adicionales del periodo.",
    )
    cuenta_pago = forms.ChoiceField(choices=CUENTA_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
