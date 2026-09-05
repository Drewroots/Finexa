import csv
import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from .models import MovimientoBancario, MovimientoContable

CUENTAS_CAJA_BANCOS = ["1105", "1110"]
TOLERANCIA_DIAS = 3


def importar_extracto_csv(empresa, archivo):
    """Parsea un CSV con columnas fecha,descripcion,valor y crea MovimientoBancario.

    fecha en formato YYYY-MM-DD. valor positivo = consignación, negativo = retiro.
    Devuelve (creados, errores) donde `errores` es una lista de strings por fila inválida.
    """
    contenido = archivo.read().decode("utf-8-sig")
    lector = csv.DictReader(io.StringIO(contenido))

    creados = 0
    errores = []
    for numero_fila, fila in enumerate(lector, start=2):
        try:
            fecha = date.fromisoformat(fila["fecha"].strip())
            descripcion = fila["descripcion"].strip()
            valor = Decimal(fila["valor"].strip())
        except (KeyError, ValueError, InvalidOperation):
            errores.append(f"Fila {numero_fila}: datos inválidos ({fila}).")
            continue

        MovimientoBancario.objects.create(
            empresa=empresa, fecha=fecha, descripcion=descripcion, valor=valor
        )
        creados += 1

    return creados, errores


def conciliar_automatico(empresa):
    """Empareja movimientos bancarios sin conciliar con movimientos contables de
    Caja/Bancos por fecha (± TOLERANCIA_DIAS) y monto exacto. Devuelve cuántos se
    conciliaron.
    """
    pendientes = MovimientoBancario.objects.filter(empresa=empresa, conciliado=False)
    candidatos = MovimientoContable.objects.filter(
        cuenta__empresa=empresa,
        cuenta__codigo__in=CUENTAS_CAJA_BANCOS,
        conciliacion_bancaria__isnull=True,
    ).select_related("transaccion")

    conciliados = 0
    for movimiento in pendientes:
        monto = abs(movimiento.valor)
        es_ingreso = movimiento.valor > 0
        rango_inicio = movimiento.fecha - timedelta(days=TOLERANCIA_DIAS)
        rango_fin = movimiento.fecha + timedelta(days=TOLERANCIA_DIAS)

        if es_ingreso:
            posibles = candidatos.filter(debito=monto, transaccion__fecha__range=(rango_inicio, rango_fin))
        else:
            posibles = candidatos.filter(credito=monto, transaccion__fecha__range=(rango_inicio, rango_fin))

        posibles = list(posibles[:2])
        if len(posibles) == 1:
            movimiento.movimiento_contable = posibles[0]
            movimiento.conciliado = True
            movimiento.save(update_fields=["movimiento_contable", "conciliado"])
            conciliados += 1

    return conciliados


def conciliar_manual(movimiento_bancario, movimiento_contable):
    ya_usado = (
        MovimientoBancario.objects.filter(movimiento_contable=movimiento_contable)
        .exclude(pk=movimiento_bancario.pk)
        .exists()
    )
    if ya_usado:
        raise ValidationError("Ese movimiento contable ya está conciliado con otro movimiento bancario.")
    movimiento_bancario.movimiento_contable = movimiento_contable
    movimiento_bancario.conciliado = True
    movimiento_bancario.save(update_fields=["movimiento_contable", "conciliado"])
