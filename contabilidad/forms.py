from django import forms


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
