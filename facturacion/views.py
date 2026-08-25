from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from core.mixins import EmpresaQuerysetMixin

from .forms import FacturaForm, FacturaItemFormSet, PagoForm
from .models import Factura
from .services import asignar_numero_factura, recalcular_totales, emitir_factura, registrar_pago


class FacturaListView(EmpresaQuerysetMixin, ListView):
    model = Factura
    template_name = "facturacion/factura_list.html"
    context_object_name = "facturas"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related("cliente").order_by("-fecha_emision", "-numero")


class FacturaDetailView(EmpresaQuerysetMixin, DetailView):
    model = Factura
    template_name = "facturacion/factura_detail.html"
    context_object_name = "factura"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pago_form"] = PagoForm()
        return ctx


@login_required
def factura_crear(request):
    empresa = request.empresa

    if request.method == "POST":
        form = FacturaForm(request.POST, empresa=empresa)
        formset_valido = False
        factura = None

        if form.is_valid():
            with transaction.atomic():
                factura = form.save(commit=False)
                factura.empresa = empresa
                factura.usuario = request.user
                asignar_numero_factura(factura)

                formset = FacturaItemFormSet(
                    request.POST, instance=factura, form_kwargs={"empresa": empresa}
                )
                if formset.is_valid() and any(
                    f.cleaned_data and not f.cleaned_data.get("DELETE") for f in formset.forms
                ):
                    formset.save()
                    recalcular_totales(factura)
                    formset_valido = True
                else:
                    if not formset.non_form_errors() and formset.is_valid():
                        formset.add_error(None, "Agrega al menos un ítem a la factura.")
                    transaction.set_rollback(True)

            if formset_valido:
                messages.success(request, f"Factura #{factura.numero:05d} creada en borrador.")
                return redirect("facturacion:detalle", pk=factura.pk)
        else:
            formset = FacturaItemFormSet(request.POST, form_kwargs={"empresa": empresa})
    else:
        form = FacturaForm(empresa=empresa)
        formset = FacturaItemFormSet(form_kwargs={"empresa": empresa})

    return render(request, "facturacion/factura_form.html", {"form": form, "formset": formset})


@login_required
def factura_emitir(request, pk):
    factura = get_object_or_404(Factura, pk=pk, empresa=request.empresa)
    if request.method == "POST":
        try:
            emitir_factura(factura, usuario=request.user)
            messages.success(request, f"Factura #{factura.numero:05d} emitida correctamente.")
        except ValidationError as exc:
            messages.error(request, exc.message if hasattr(exc, "message") else str(exc))
    return redirect("facturacion:detalle", pk=pk)


@login_required
def factura_pagar(request, pk):
    factura = get_object_or_404(Factura, pk=pk, empresa=request.empresa)
    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            try:
                registrar_pago(
                    factura,
                    monto=form.cleaned_data["monto"],
                    cuenta_destino_codigo=form.cleaned_data["cuenta_destino"],
                    usuario=request.user,
                )
                messages.success(request, "Pago registrado correctamente.")
            except ValidationError as exc:
                messages.error(request, exc.message if hasattr(exc, "message") else str(exc))
    return redirect("facturacion:detalle", pk=pk)
