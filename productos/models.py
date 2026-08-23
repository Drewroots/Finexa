from decimal import Decimal

from django.db import models

from core.models import Empresa, Usuario


class Producto(models.Model):
    TIPO_CHOICES = [
        ("PRODUCTO", "Producto (con inventario)"),
        ("SERVICIO", "Servicio"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="productos")
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="PRODUCTO")
    precio_venta = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    costo = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("19"))
    unidad_medida = models.CharField(max_length=20, default="UND")
    stock_actual = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    stock_minimo = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]
        unique_together = ("empresa", "codigo")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def bajo_stock_minimo(self):
        return self.tipo == "PRODUCTO" and self.stock_actual <= self.stock_minimo


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="movimientos_inventario")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=14, decimal_places=2)
    motivo = models.CharField(max_length=200, blank=True)
    referencia = models.CharField(max_length=100, blank=True, help_text="Ej: Factura #0001")
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} {self.cantidad} - {self.producto}"
