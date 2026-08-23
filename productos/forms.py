from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "tipo",
            "precio_venta",
            "costo",
            "porcentaje_iva",
            "unidad_medida",
            "stock_actual",
            "stock_minimo",
            "activo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "precio_venta": forms.NumberInput(attrs={"class": "form-control"}),
            "costo": forms.NumberInput(attrs={"class": "form-control"}),
            "porcentaje_iva": forms.NumberInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.TextInput(attrs={"class": "form-control"}),
            "stock_actual": forms.NumberInput(attrs={"class": "form-control"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
