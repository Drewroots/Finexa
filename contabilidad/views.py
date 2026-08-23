from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView

from core.mixins import EmpresaQuerysetMixin

from .models import CuentaContable, Transaccion


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
