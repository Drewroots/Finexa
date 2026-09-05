from django import forms
from django.forms import inlineformset_factory

from .models import Factura, FacturaItem


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ["cliente", "fecha_emision", "fecha_vencimiento", "notas"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "fecha_emision": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa is not None:
            self.fields["cliente"].queryset = self.fields["cliente"].queryset.filter(
                empresa=empresa, activo=True
            )


class FacturaItemForm(forms.ModelForm):
    class Meta:
        model = FacturaItem
        fields = ["producto", "bodega", "cantidad", "precio_unitario", "porcentaje_iva"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "bodega": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "porcentaje_iva": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bodega"].required = False
        if empresa is not None:
            self.fields["producto"].queryset = self.fields["producto"].queryset.filter(
                empresa=empresa, activo=True
            )
            self.fields["bodega"].queryset = self.fields["bodega"].queryset.filter(
                empresa=empresa, activa=True
            )


FacturaItemFormSet = inlineformset_factory(
    Factura,
    FacturaItem,
    form=FacturaItemForm,
    extra=3,
    can_delete=True,
)


class PagoForm(forms.Form):
    CUENTA_CHOICES = [("1105", "Caja"), ("1110", "Bancos")]

    monto = forms.DecimalField(max_digits=14, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control"}))
    cuenta_destino = forms.ChoiceField(choices=CUENTA_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))


class NotaCreditoDebitoForm(forms.Form):
    TIPO_CHOICES = [("CREDITO", "Nota crédito"), ("DEBITO", "Nota débito")]

    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    valor = forms.DecimalField(max_digits=14, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control"}))
    motivo = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
