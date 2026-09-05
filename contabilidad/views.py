from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from core.mixins import EmpresaQuerysetMixin

from .models import CuentaContable, TareaCierre, Transaccion
from .services import calcular_balance_general, calcular_estado_resultados
from .cierre import TAREAS_CIERRE_BASE, obtener_o_crear_checklist


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
