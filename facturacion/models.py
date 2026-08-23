from decimal import Decimal

from django.db import models

from clientes.models import Tercero
from core.models import Empresa, Usuario
from productos.models import Producto


class Factura(models.Model):
    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("EMITIDA", "Emitida"),
        ("PAGADA", "Pagada"),
        ("ANULADA", "Anulada"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="facturas")
    numero = models.PositiveIntegerField()
    cliente = models.ForeignKey(Tercero, on_delete=models.PROTECT, related_name="facturas")
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="BORRADOR")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    iva = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    saldo_pendiente = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    notas = models.TextField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-fecha_emision", "-numero"]
        unique_together = ("empresa", "numero")

    def __str__(self):
        return f"Factura #{self.numero:05d} - {self.cliente.razon_social}"

    @property
    def vencida(self):
        from django.utils import timezone

        return (
            self.estado == "EMITIDA"
            and self.saldo_pendiente > 0
            and self.fecha_vencimiento < timezone.localdate()
        )


class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="items_factura")
    cantidad = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("1"))
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("19"))

    class Meta:
        verbose_name = "Ítem de factura"
        verbose_name_plural = "Ítems de factura"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def valor_iva(self):
        return self.subtotal * self.porcentaje_iva / Decimal("100")

    @property
    def total(self):
        return self.subtotal + self.valor_iva

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
