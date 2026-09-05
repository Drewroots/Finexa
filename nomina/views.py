from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import EmpresaFormMixin, EmpresaQuerysetMixin

from .forms import EmpleadoForm, LiquidarNominaForm
from .models import Empleado, Liquidacion
from .services import liquidar_nomina


class EmpleadoListView(EmpresaQuerysetMixin, ListView):
    model = Empleado
    template_name = "nomina/empleado_list.html"
    context_object_name = "empleados"

    def get_queryset(self):
        return super().get_queryset().order_by("nombre_completo")


class EmpleadoCreateView(EmpresaFormMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "nomina/empleado_form.html"
    success_url = reverse_lazy("nomina:empleados")


class EmpleadoUpdateView(EmpresaQuerysetMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "nomina/empleado_form.html"
    success_url = reverse_lazy("nomina:empleados")


class EmpleadoDetailView(EmpresaQuerysetMixin, DetailView):
    model = Empleado
    template_name = "nomina/empleado_detail.html"
    context_object_name = "empleado"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["liquidaciones"] = self.object.liquidaciones.order_by("-anio", "-mes")
        ctx["form"] = LiquidarNominaForm()
        return ctx


@login_required
def liquidar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk, empresa=request.empresa)
    if request.method == "POST":
        form = LiquidarNominaForm(request.POST)
        if form.is_valid():
            try:
                liquidar_nomina(
                    empleado,
                    anio=form.cleaned_data["anio"],
                    mes=int(form.cleaned_data["mes"]),
                    dias_trabajados=form.cleaned_data["dias_trabajados"],
                    otros_devengados=form.cleaned_data["otros_devengados"] or 0,
                    usuario=request.user,
                    cuenta_pago_codigo=form.cleaned_data["cuenta_pago"],
                )
                messages.success(request, "Nómina liquidada correctamente.")
            except ValidationError as exc:
                messages.error(request, exc.message if hasattr(exc, "message") else str(exc))
    return redirect("nomina:empleado_detalle", pk=pk)


class LiquidacionDetailView(EmpresaQuerysetMixin, DetailView):
    model = Liquidacion
    template_name = "nomina/liquidacion_detail.html"
    context_object_name = "liquidacion"
