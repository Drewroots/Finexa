from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .models import Bodega, MovimientoInventario, StockPorBodega


def obtener_bodega_principal(empresa):
    """Bodega por defecto de una empresa; se crea la primera vez que se necesita."""
    bodega, _ = Bodega.objects.get_or_create(empresa=empresa, nombre="Principal")
    return bodega


@transaction.atomic
def registrar_movimiento(producto, tipo, cantidad, bodega=None, usuario=None, motivo="", referencia=""):
    """Crea un MovimientoInventario y ajusta el stock de la bodega y el total del producto.

    Si no se especifica `bodega`, se usa la bodega "Principal" de la empresa (HU-14).
    `Producto.stock_actual` se mantiene como la suma de todas sus bodegas, para no
    romper el resto del sistema (KPIs, alertas de stock minimo) que lo lee directamente.
    """
    bodega = bodega or obtener_bodega_principal(producto.empresa)

    stock, _ = StockPorBodega.objects.select_for_update().get_or_create(producto=producto, bodega=bodega)
    if tipo == "SALIDA":
        stock.cantidad -= cantidad
    else:
        stock.cantidad += cantidad
    stock.save(update_fields=["cantidad"])

    producto.stock_actual = producto.stock_por_bodega.aggregate(total=Sum("cantidad"))["total"] or Decimal("0")
    producto.save(update_fields=["stock_actual"])

    return MovimientoInventario.objects.create(
        empresa=producto.empresa,
        producto=producto,
        bodega=bodega,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo,
        referencia=referencia,
        usuario=usuario,
    )
