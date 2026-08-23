from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import CuentaContable, MovimientoContable, Transaccion

# Plan de cuentas base (subconjunto simplificado del PUC colombiano) que se
# crea automáticamente para cada empresa nueva y que usan los demás módulos
# (facturación, inventario) para generar asientos automáticos.
PLAN_CUENTAS_BASE = [
    ("1105", "Caja", "ACTIVO", "DEBITO"),
    ("1110", "Bancos", "ACTIVO", "DEBITO"),
    ("1305", "Clientes (Cuentas por cobrar)", "ACTIVO", "DEBITO"),
    ("1435", "Inventarios", "ACTIVO", "DEBITO"),
    ("2205", "Proveedores (Cuentas por pagar)", "PASIVO", "CREDITO"),
    ("2408", "IVA por pagar", "PASIVO", "CREDITO"),
    ("2365", "Retenciones y aportes de nómina por pagar", "PASIVO", "CREDITO"),
    ("3105", "Capital social", "PATRIMONIO", "CREDITO"),
    ("4135", "Ingresos por ventas", "INGRESO", "CREDITO"),
    ("5135", "Gastos generales", "GASTO", "DEBITO"),
    ("6135", "Costo de ventas", "COSTO", "DEBITO"),
    ("5105", "Gastos de personal (nómina)", "GASTO", "DEBITO"),
]

# Códigos usados por otros módulos para no acoplarse a strings sueltos.
CUENTA_CLIENTES = "1305"
CUENTA_INVENTARIOS = "1435"
CUENTA_IVA_POR_PAGAR = "2408"
CUENTA_INGRESOS_VENTAS = "4135"
CUENTA_COSTO_VENTAS = "6135"


def sembrar_plan_cuentas(empresa):
    """Crea el plan de cuentas base para una empresa nueva (idempotente)."""
    for codigo, nombre, tipo, naturaleza in PLAN_CUENTAS_BASE:
        CuentaContable.objects.get_or_create(
            empresa=empresa,
            codigo=codigo,
            defaults={"nombre": nombre, "tipo": tipo, "naturaleza": naturaleza},
        )


@transaction.atomic
def crear_transaccion(empresa, fecha, descripcion, lineas, documento_origen="", usuario=None):
    """Crea un asiento contable de partida doble.

    `lineas` es una lista de tuplas (codigo_cuenta, debito, credito).
    Lanza ValidationError si el asiento no cuadra (total débitos != total créditos).
    """
    total_debitos = sum((Decimal(d) for _, d, _ in lineas), Decimal("0"))
    total_creditos = sum((Decimal(c) for _, _, c in lineas), Decimal("0"))
    if total_debitos != total_creditos:
        raise ValidationError(
            f"El asiento no cuadra: débitos={total_debitos} créditos={total_creditos}"
        )

    transaccion = Transaccion.objects.create(
        empresa=empresa,
        fecha=fecha,
        descripcion=descripcion,
        documento_origen=documento_origen,
        usuario=usuario,
    )
    for codigo_cuenta, debito, credito in lineas:
        cuenta = CuentaContable.objects.get(empresa=empresa, codigo=codigo_cuenta)
        MovimientoContable.objects.create(
            transaccion=transaccion, cuenta=cuenta, debito=debito, credito=credito
        )
    return transaccion
