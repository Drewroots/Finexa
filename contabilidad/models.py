from decimal import Decimal

from django.db import models

from core.models import Empresa, Usuario


class CuentaContable(models.Model):
    """Plan Único de Cuentas simplificado (base NIIF para pymes)."""

    TIPO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("PASIVO", "Pasivo"),
        ("PATRIMONIO", "Patrimonio"),
        ("INGRESO", "Ingreso"),
        ("GASTO", "Gasto"),
        ("COSTO", "Costo"),
    ]
    NATURALEZA_CHOICES = [("DEBITO", "Débito"), ("CREDITO", "Crédito")]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="cuentas")
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    naturaleza = models.CharField(max_length=10, choices=NATURALEZA_CHOICES)
    cuenta_padre = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subcuentas"
    )
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"
        ordering = ["codigo"]
        unique_together = ("empresa", "codigo")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Transaccion(models.Model):
    """Un asiento contable (cabecera) compuesto por varios movimientos de partida doble."""

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="transacciones")
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    documento_origen = models.CharField(
        max_length=100, blank=True, help_text="Ej: Factura #0001, Nómina agosto 2026"
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"

    @property
    def total_debitos(self):
        return sum((m.debito for m in self.movimientos.all()), Decimal("0"))

    @property
    def total_creditos(self):
        return sum((m.credito for m in self.movimientos.all()), Decimal("0"))

    @property
    def cuadrada(self):
        return self.total_debitos == self.total_creditos


class MovimientoContable(models.Model):
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name="movimientos")
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, related_name="movimientos")
    debito = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    credito = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))

    class Meta:
        verbose_name = "Movimiento contable"
        verbose_name_plural = "Movimientos contables"

    def __str__(self):
        return f"{self.cuenta.codigo} D:{self.debito} C:{self.credito}"
