from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum

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
CUENTA_CAJA = "1105"
CUENTA_BANCOS = "1110"
CUENTA_CLIENTES = "1305"
CUENTA_INVENTARIOS = "1435"
CUENTA_APORTES_NOMINA_POR_PAGAR = "2365"
CUENTA_IVA_POR_PAGAR = "2408"
CUENTA_INGRESOS_VENTAS = "4135"
CUENTA_GASTO_NOMINA = "5105"
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


def _saldo_por_tipo(empresa, tipos, fecha_inicio=None, fecha_fin=None):
    """Suma débitos/créditos de las cuentas de los `tipos` dados, en el rango de fechas."""
    movimientos = MovimientoContable.objects.filter(cuenta__empresa=empresa, cuenta__tipo__in=tipos)
    if fecha_inicio:
        movimientos = movimientos.filter(transaccion__fecha__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(transaccion__fecha__lte=fecha_fin)
    agregados = movimientos.aggregate(debito=Sum("debito"), credito=Sum("credito"))
    return agregados["debito"] or Decimal("0"), agregados["credito"] or Decimal("0")


def calcular_estado_resultados(empresa, fecha_inicio, fecha_fin):
    """Estado de resultados (P&G) simplificado: Ingresos - Costos - Gastos = Utilidad neta."""
    debito_ing, credito_ing = _saldo_por_tipo(empresa, ["INGRESO"], fecha_inicio, fecha_fin)
    debito_costo, credito_costo = _saldo_por_tipo(empresa, ["COSTO"], fecha_inicio, fecha_fin)
    debito_gasto, credito_gasto = _saldo_por_tipo(empresa, ["GASTO"], fecha_inicio, fecha_fin)

    ingresos = credito_ing - debito_ing
    costos = debito_costo - credito_costo
    gastos = debito_gasto - credito_gasto
    utilidad_bruta = ingresos - costos
    utilidad_neta = utilidad_bruta - gastos

    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "ingresos": ingresos,
        "costos": costos,
        "utilidad_bruta": utilidad_bruta,
        "gastos": gastos,
        "utilidad_neta": utilidad_neta,
    }


def calcular_balance_general(empresa, fecha_corte):
    """Balance general simplificado agrupado por tipo de cuenta, a una fecha de corte.

    La utilidad del ejercicio (ingresos - costos - gastos desde el inicio hasta la
    fecha de corte) se suma como una linea mas de Patrimonio para que la ecuacion
    Activo = Pasivo + Patrimonio cuadre, ya que el modelo no hace cierre contable
    formal de INGRESO/GASTO/COSTO contra Patrimonio al final de cada periodo.
    """
    grupos = {}
    for tipo, _ in CuentaContable.TIPO_CHOICES:
        if tipo not in ("ACTIVO", "PASIVO", "PATRIMONIO"):
            continue
        cuentas = CuentaContable.objects.filter(empresa=empresa, tipo=tipo).annotate(
            total_debito=Sum("movimientos__debito", filter=Q(movimientos__transaccion__fecha__lte=fecha_corte)),
            total_credito=Sum("movimientos__credito", filter=Q(movimientos__transaccion__fecha__lte=fecha_corte)),
        ).order_by("codigo")
        filas = []
        total_grupo = Decimal("0")
        for cuenta in cuentas:
            debito = cuenta.total_debito or Decimal("0")
            credito = cuenta.total_credito or Decimal("0")
            saldo = (debito - credito) if cuenta.naturaleza == "DEBITO" else (credito - debito)
            filas.append({"cuenta": cuenta, "saldo": saldo})
            total_grupo += saldo
        grupos[tipo] = {"filas": filas, "total": total_grupo}

    estado_resultados = calcular_estado_resultados(empresa, fecha_inicio=None, fecha_fin=fecha_corte)
    utilidad_neta = estado_resultados["utilidad_neta"]
    grupos["PATRIMONIO"]["filas"].append(
        {"cuenta": None, "saldo": utilidad_neta, "nombre": "Utilidad del ejercicio (acumulada)"}
    )
    grupos["PATRIMONIO"]["total"] += utilidad_neta

    return {
        "fecha_corte": fecha_corte,
        "activo": grupos["ACTIVO"],
        "pasivo": grupos["PASIVO"],
        "patrimonio": grupos["PATRIMONIO"],
        "total_pasivo_patrimonio": grupos["PASIVO"]["total"] + grupos["PATRIMONIO"]["total"],
    }
