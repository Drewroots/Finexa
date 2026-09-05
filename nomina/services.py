from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from contabilidad.services import (
    CUENTA_APORTES_NOMINA_POR_PAGAR,
    CUENTA_GASTO_NOMINA,
    crear_transaccion,
)

from .models import Liquidacion

# Tarifas de referencia 2026 (Colombia). Ajustar si la ley/decreto cambia.
PORCENTAJE_SALUD_EMPLEADO = Decimal("4")
PORCENTAJE_PENSION_EMPLEADO = Decimal("4")
PORCENTAJE_SALUD_EMPLEADOR = Decimal("8.5")
PORCENTAJE_PENSION_EMPLEADOR = Decimal("12")
PORCENTAJE_ARL_CLASE_I = Decimal("0.522")
PORCENTAJE_CAJA_COMPENSACION = Decimal("4")
PORCENTAJE_CESANTIAS = Decimal("8.33")
PORCENTAJE_INTERESES_CESANTIAS = Decimal("1")
PORCENTAJE_PRIMA = Decimal("8.33")
PORCENTAJE_VACACIONES = Decimal("4.17")


def _redondear(valor):
    return valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


@transaction.atomic
def liquidar_nomina(
    empleado,
    anio,
    mes,
    dias_trabajados=30,
    otros_devengados=Decimal("0"),
    usuario=None,
    fecha_pago=None,
    cuenta_pago_codigo="1105",
):
    """Liquida la nómina de un empleado para un periodo y genera su asiento contable.

    Cubre deducciones de ley (salud/pensión del empleado) y provisión de aportes
    patronales y prestaciones sociales. No genera el documento electrónico de
    nómina ante la DIAN (eso requiere un Proveedor Tecnológico Autorizado, HU-29).
    """
    if Liquidacion.objects.filter(empleado=empleado, anio=anio, mes=mes).exists():
        raise ValidationError("Ya existe una liquidación para este empleado en este periodo.")
    if dias_trabajados <= 0 or dias_trabajados > 30:
        raise ValidationError("Los días trabajados deben estar entre 1 y 30.")

    fecha_pago = fecha_pago or timezone.localdate()
    salario_base = empleado.salario_base
    proporcion = Decimal(dias_trabajados) / Decimal("30")

    devengado_salario = _redondear(salario_base * proporcion)
    auxilio_transporte = Decimal("0")
    if salario_base <= settings.SALARIO_MINIMO_LEGAL * 2:
        auxilio_transporte = _redondear(settings.AUXILIO_TRANSPORTE * proporcion)

    total_devengado = devengado_salario + auxilio_transporte + otros_devengados

    # Deducciones al empleado: se calculan sobre el salario devengado (sin auxilio de transporte).
    base_aportes = devengado_salario
    salud_empleado = _redondear(base_aportes * PORCENTAJE_SALUD_EMPLEADO / 100)
    pension_empleado = _redondear(base_aportes * PORCENTAJE_PENSION_EMPLEADO / 100)
    total_deducciones = salud_empleado + pension_empleado
    neto_pagado = total_devengado - total_deducciones

    # Aportes patronales y provisión de prestaciones sociales: son gasto y pasivo
    # de la empresa, no afectan lo que recibe el empleado.
    salud_empleador = _redondear(base_aportes * PORCENTAJE_SALUD_EMPLEADOR / 100)
    pension_empleador = _redondear(base_aportes * PORCENTAJE_PENSION_EMPLEADOR / 100)
    arl = _redondear(base_aportes * PORCENTAJE_ARL_CLASE_I / 100)
    caja_compensacion = _redondear(base_aportes * PORCENTAJE_CAJA_COMPENSACION / 100)
    cesantias = _redondear(total_devengado * PORCENTAJE_CESANTIAS / 100)
    intereses_cesantias = _redondear(cesantias * PORCENTAJE_INTERESES_CESANTIAS / 100)
    prima = _redondear(total_devengado * PORCENTAJE_PRIMA / 100)
    vacaciones = _redondear(base_aportes * PORCENTAJE_VACACIONES / 100)

    total_aportes_y_prestaciones = (
        salud_empleador + pension_empleador + arl + caja_compensacion
        + cesantias + intereses_cesantias + prima + vacaciones
    )

    gasto_total = total_devengado + total_aportes_y_prestaciones
    pasivo_aportes = total_deducciones + total_aportes_y_prestaciones

    lineas = [
        (CUENTA_GASTO_NOMINA, gasto_total, Decimal("0")),
        (CUENTA_APORTES_NOMINA_POR_PAGAR, Decimal("0"), pasivo_aportes),
        (cuenta_pago_codigo, Decimal("0"), neto_pagado),
    ]

    transaccion = crear_transaccion(
        empresa=empleado.empresa,
        fecha=fecha_pago,
        descripcion=f"Nómina {mes:02d}/{anio} - {empleado.nombre_completo}",
        lineas=lineas,
        documento_origen=f"Nómina {empleado.nombre_completo} {mes:02d}/{anio}",
        usuario=usuario,
    )

    return Liquidacion.objects.create(
        empresa=empleado.empresa,
        empleado=empleado,
        anio=anio,
        mes=mes,
        fecha_pago=fecha_pago,
        dias_trabajados=dias_trabajados,
        salario_base=salario_base,
        auxilio_transporte=auxilio_transporte,
        otros_devengados=otros_devengados,
        total_devengado=total_devengado,
        salud_empleado=salud_empleado,
        pension_empleado=pension_empleado,
        total_deducciones=total_deducciones,
        neto_pagado=neto_pagado,
        salud_empleador=salud_empleador,
        pension_empleador=pension_empleador,
        arl=arl,
        caja_compensacion=caja_compensacion,
        cesantias=cesantias,
        intereses_cesantias=intereses_cesantias,
        prima=prima,
        vacaciones=vacaciones,
        usuario=usuario,
        transaccion=transaccion,
    )
