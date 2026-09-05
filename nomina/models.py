from decimal import Decimal

from django.db import models

from core.models import Empresa, Usuario


class Empleado(models.Model):
    """Empleado de nómina de una empresa (HU-28). Independiente de Usuario del sistema."""

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="empleados")
    nombre_completo = models.CharField(max_length=200)
    numero_documento = models.CharField(max_length=20)
    cargo = models.CharField(max_length=100, blank=True)
    salario_base = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["nombre_completo"]
        unique_together = ("empresa", "numero_documento")

    def __str__(self):
        return f"{self.nombre_completo} ({self.numero_documento})"


class Liquidacion(models.Model):
    """Liquidación de nómina de un empleado para un periodo mensual (HU-28).

    Cumple seguridad social (salud/pensión) y provisión de prestaciones sociales
    (cesantías, intereses, prima, vacaciones) según tarifas configurables en
    nomina/services.py. No genera el documento electrónico ante la DIAN (HU-29):
    eso requiere una integración externa con un Proveedor Tecnológico Autorizado.
    """

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="liquidaciones_nomina")
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name="liquidaciones")
    anio = models.PositiveIntegerField()
    mes = models.PositiveSmallIntegerField()
    fecha_pago = models.DateField()
    dias_trabajados = models.PositiveSmallIntegerField(default=30)

    salario_base = models.DecimalField(max_digits=14, decimal_places=2)
    auxilio_transporte = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    otros_devengados = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_devengado = models.DecimalField(max_digits=14, decimal_places=2)

    salud_empleado = models.DecimalField(max_digits=14, decimal_places=2)
    pension_empleado = models.DecimalField(max_digits=14, decimal_places=2)
    total_deducciones = models.DecimalField(max_digits=14, decimal_places=2)
    neto_pagado = models.DecimalField(max_digits=14, decimal_places=2)

    salud_empleador = models.DecimalField(max_digits=14, decimal_places=2)
    pension_empleador = models.DecimalField(max_digits=14, decimal_places=2)
    arl = models.DecimalField(max_digits=14, decimal_places=2)
    caja_compensacion = models.DecimalField(max_digits=14, decimal_places=2)
    cesantias = models.DecimalField(max_digits=14, decimal_places=2)
    intereses_cesantias = models.DecimalField(max_digits=14, decimal_places=2)
    prima = models.DecimalField(max_digits=14, decimal_places=2)
    vacaciones = models.DecimalField(max_digits=14, decimal_places=2)

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    transaccion = models.ForeignKey(
        "contabilidad.Transaccion", on_delete=models.PROTECT, related_name="liquidaciones_nomina"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Liquidación de nómina"
        verbose_name_plural = "Liquidaciones de nómina"
        ordering = ["-anio", "-mes"]
        unique_together = ("empleado", "anio", "mes")

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.mes:02d}/{self.anio}"

    @property
    def total_aportes_patronales_y_prestaciones(self):
        return (
            self.salud_empleador
            + self.pension_empleador
            + self.arl
            + self.caja_compensacion
            + self.cesantias
            + self.intereses_cesantias
            + self.prima
            + self.vacaciones
        )
