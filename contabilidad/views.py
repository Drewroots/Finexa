import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from core.mixins import EmpresaQuerysetMixin

from .conciliacion import conciliar_automatico, conciliar_manual, importar_extracto_csv, CUENTAS_CAJA_BANCOS
from .forms import CargarExtractoForm, ConciliarManualForm
from .models import CuentaContable, MovimientoBancario, MovimientoContable, TareaCierre, Transaccion
from .services import calcular_balance_general, calcular_estado_resultados
from .cierre import TAREAS_CIERRE_BASE, obtener_o_crear_checklist
from .puc_data import PUC_CATALOGO_PLANO


class TransaccionListView(EmpresaQuerysetMixin, ListView):
    model = Transaccion
    template_name = "contabilidad/transaccion_list.html"
    context_object_name = "transacciones"
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().prefetch_related("movimientos__cuenta")


class BalanceComprobacionView(LoginRequiredMixin, ListView):
    """Balance de comprobación: total débitos/créditos y saldo por cuenta."""

    template_name = "contabilidad/balance.html"
    context_object_name = "cuentas"

    def get_queryset(self):
        cuentas = (
            CuentaContable.objects.filter(empresa=self.request.empresa)
            .annotate(
                total_debito=Sum("movimientos__debito"),
                total_credito=Sum("movimientos__credito"),
            )
            .order_by("codigo")
        )
        resultado = []
        for cuenta in cuentas:
            debito = cuenta.total_debito or 0
            credito = cuenta.total_credito or 0
            saldo = (debito - credito) if cuenta.naturaleza == "DEBITO" else (credito - debito)
            resultado.append(
                {"cuenta": cuenta, "debito": debito, "credito": credito, "saldo": saldo}
            )
        return resultado


def _parsear_fecha(valor, por_defecto):
    if not valor:
        return por_defecto
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return por_defecto


@login_required
def estado_resultados(request):
    hoy = timezone.localdate()
    fecha_inicio = _parsear_fecha(request.GET.get("fecha_inicio"), date(hoy.year, 1, 1))
    fecha_fin = _parsear_fecha(request.GET.get("fecha_fin"), hoy)
    datos = calcular_estado_resultados(request.empresa, fecha_inicio, fecha_fin)
    return render(request, "contabilidad/estado_resultados.html", datos)


@login_required
def balance_general(request):
    hoy = timezone.localdate()
    fecha_corte = _parsear_fecha(request.GET.get("fecha_corte"), hoy)
    datos = calcular_balance_general(request.empresa, fecha_corte)
    return render(request, "contabilidad/balance_general.html", datos)


@login_required
def cierre_mensual(request):
    hoy = timezone.localdate()
    anio = int(request.GET.get("anio", hoy.year))
    mes = int(request.GET.get("mes", hoy.month))
    tareas = obtener_o_crear_checklist(request.empresa, anio, mes)
    return render(
        request,
        "contabilidad/cierre.html",
        {"tareas": tareas, "anio": anio, "mes": mes, "total": len(tareas), "completadas": sum(t.completada for t in tareas)},
    )


@login_required
def cierre_marcar_tarea(request, pk):
    tarea = get_object_or_404(TareaCierre, pk=pk, empresa=request.empresa)
    if request.method == "POST":
        tarea.completada = not tarea.completada
        tarea.completada_en = timezone.now() if tarea.completada else None
        tarea.completada_por = request.user if tarea.completada else None
        tarea.save(update_fields=["completada", "completada_en", "completada_por"])
    return redirect(f"{reverse('contabilidad:cierre')}?anio={tarea.anio}&mes={tarea.mes}")


@login_required
def conciliacion_lista(request):
    empresa = request.empresa
    if request.method == "POST":
        form = CargarExtractoForm(request.POST, request.FILES)
        if form.is_valid():
            creados, errores = importar_extracto_csv(empresa, request.FILES["archivo"])
            conciliados = conciliar_automatico(empresa)
            messages.success(
                request,
                f"Se importaron {creados} movimientos y se conciliaron automáticamente {conciliados}.",
            )
            for error in errores:
                messages.warning(request, error)
        return redirect("contabilidad:conciliacion")
    else:
        form = CargarExtractoForm()

    movimientos = MovimientoBancario.objects.filter(empresa=empresa).order_by("-fecha")
    candidatos = MovimientoContable.objects.filter(
        cuenta__empresa=empresa, cuenta__codigo__in=CUENTAS_CAJA_BANCOS, conciliacion_bancaria__isnull=True
    ).select_related("cuenta", "transaccion")
    opciones = [(m.pk, f"{m.transaccion.fecha} · {m.cuenta.nombre} · D:{m.debito} C:{m.credito} · {m.transaccion.descripcion}") for m in candidatos]

    return render(
        request,
        "contabilidad/conciliacion.html",
        {"form": form, "movimientos": movimientos, "manual_form": ConciliarManualForm(opciones=opciones)},
    )


@login_required
def conciliacion_marcar_manual(request, pk):
    movimiento = get_object_or_404(MovimientoBancario, pk=pk, empresa=request.empresa)
    if request.method == "POST":
        candidatos = MovimientoContable.objects.filter(
            cuenta__empresa=request.empresa, cuenta__codigo__in=CUENTAS_CAJA_BANCOS
        )
        opciones = [(m.pk, str(m.pk)) for m in candidatos]
        form = ConciliarManualForm(request.POST, opciones=opciones)
        if form.is_valid():
            movimiento_contable = get_object_or_404(
                MovimientoContable, pk=form.cleaned_data["movimiento_contable"], cuenta__empresa=request.empresa
            )
            try:
                conciliar_manual(movimiento, movimiento_contable)
                messages.success(request, "Movimiento conciliado.")
            except ValidationError as exc:
                messages.error(request, str(exc))
    return redirect("contabilidad:conciliacion")


@login_required
def puc_referencia(request):
    """Panel de ayuda: catalogo completo del PUC (Decreto 2650) a nivel de
    clase/grupo/cuenta, como referencia de consulta (no depende de la empresa)."""
    clases = []
    for codigo, clase in sorted(
        ((f["clase"], f) for f in PUC_CATALOGO_PLANO if f["nivel"] == "clase"),
        key=lambda par: par[0],
    ):
        cuentas_y_grupos = [
            f for f in PUC_CATALOGO_PLANO
            if f["clase"] == codigo and f["nivel"] in ("grupo", "cuenta")
        ]
        clases.append({"codigo": codigo, "nombre": clase["nombre"], "filas": cuentas_y_grupos})
    return render(request, "contabilidad/puc_referencia.html", {"clases": clases})


@login_required
def puc_descargar_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = "attachment; filename=puc_decreto_2650.csv"
    writer = csv.writer(response)
    writer.writerow(["codigo", "nombre", "nivel", "clase", "clase_nombre", "grupo", "grupo_nombre", "naturaleza"])
    for fila in PUC_CATALOGO_PLANO:
        writer.writerow([
            fila["codigo"], fila["nombre"], fila["nivel"], fila["clase"], fila["clase_nombre"],
            fila["grupo"], fila["grupo_nombre"], fila["naturaleza"],
        ])
    return response
