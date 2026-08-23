"""KPIs y asistente de negocio basado en reglas (v0).

La propuesta de valor de NovaERP incluye un asistente conversacional con IA
(ver docs/ROADMAP.md, fase 6). Esta primera versión resuelve un conjunto
acotado de preguntas frecuentes con reglas simples sobre los datos reales de
la empresa, sin depender de un proveedor externo de LLM, para poder demostrar
el flujo de punta a punta desde ya.
"""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from contabilidad.models import CuentaContable
from contabilidad.services import CUENTA_IVA_POR_PAGAR
from facturacion.models import Factura
from productos.models import Producto


def calcular_kpis(empresa):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    ventas_mes = (
        Factura.objects.filter(
            empresa=empresa, estado__in=["EMITIDA", "PAGADA"], fecha_emision__gte=inicio_mes
        ).aggregate(total=Sum("total"))["total"]
        or Decimal("0")
    )

    cuentas_por_cobrar = (
        Factura.objects.filter(empresa=empresa, estado="EMITIDA").aggregate(
            total=Sum("saldo_pendiente")
        )["total"]
        or Decimal("0")
    )

    facturas_vencidas = [
        f
        for f in Factura.objects.filter(
            empresa=empresa, estado="EMITIDA", fecha_vencimiento__lt=hoy
        )
    ]

    productos_bajo_stock = [
        p for p in Producto.objects.filter(empresa=empresa, tipo="PRODUCTO", activo=True)
        if p.bajo_stock_minimo
    ]

    flujo_proyectado = {}
    for dias in (30, 60, 90):
        limite = hoy + timedelta(days=dias)
        total = (
            Factura.objects.filter(
                empresa=empresa,
                estado="EMITIDA",
                fecha_vencimiento__gte=hoy,
                fecha_vencimiento__lte=limite,
            ).aggregate(total=Sum("saldo_pendiente"))["total"]
            or Decimal("0")
        )
        flujo_proyectado[dias] = total

    return {
        "ventas_mes": ventas_mes,
        "cuentas_por_cobrar": cuentas_por_cobrar,
        "facturas_vencidas": facturas_vencidas,
        "productos_bajo_stock": productos_bajo_stock,
        "flujo_proyectado": flujo_proyectado,
        "impuestos_por_pagar": saldo_cuenta(empresa, CUENTA_IVA_POR_PAGAR),
    }


def saldo_cuenta(empresa, codigo_cuenta):
    try:
        cuenta = CuentaContable.objects.get(empresa=empresa, codigo=codigo_cuenta)
    except CuentaContable.DoesNotExist:
        return Decimal("0")
    agregados = cuenta.movimientos.aggregate(debito=Sum("debito"), credito=Sum("credito"))
    debito = agregados["debito"] or Decimal("0")
    credito = agregados["credito"] or Decimal("0")
    return (debito - credito) if cuenta.naturaleza == "DEBITO" else (credito - debito)


def asistente_responder(empresa, pregunta):
    pregunta = pregunta.lower()
    kpis = calcular_kpis(empresa)

    if "impuesto" in pregunta or "iva" in pregunta:
        return f"Actualmente tienes ${kpis['impuestos_por_pagar']:,.0f} de IVA por pagar acumulado."
    if "cobrar" in pregunta or "cartera" in pregunta:
        n_vencidas = len(kpis["facturas_vencidas"])
        return (
            f"Tienes ${kpis['cuentas_por_cobrar']:,.0f} en cartera pendiente, "
            f"de los cuales {n_vencidas} factura(s) ya están vencidas."
        )
    if "stock" in pregunta or "inventario" in pregunta:
        n = len(kpis["productos_bajo_stock"])
        if n == 0:
            return "Ningún producto está por debajo de su stock mínimo."
        nombres = ", ".join(p.nombre for p in kpis["productos_bajo_stock"][:5])
        return f"Tienes {n} producto(s) en o bajo el stock mínimo, por ejemplo: {nombres}."
    if "venta" in pregunta:
        return f"Las ventas de este mes suman ${kpis['ventas_mes']:,.0f}."
    if "caja" in pregunta or "flujo" in pregunta:
        f = kpis["flujo_proyectado"]
        return (
            f"Flujo de caja proyectado por cobrar: 30 días ${f[30]:,.0f}, "
            f"60 días ${f[60]:,.0f}, 90 días ${f[90]:,.0f}."
        )
    return (
        "Puedo responder sobre impuestos, cartera por cobrar, inventario, ventas o flujo de "
        "caja. Prueba, por ejemplo: '¿cuánto debo en impuestos este mes?'"
    )
