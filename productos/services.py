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
    bodega_principal = obtener_bodega_principal(producto.empresa)
    bodega = bodega or bodega_principal

    # Si el producto ya tenia `stock_actual` sin desglosar por bodega (p.ej. uno
    # recien creado), ese saldo se asume en la bodega principal la primera vez
    # que se le registra un movimiento, en vez de arrancar en cero.
    valor_inicial = producto.stock_actual if bodega.pk == bodega_principal.pk else Decimal("0")
    stock, _ = StockPorBodega.objects.select_for_update().get_or_create(
        producto=producto, bodega=bodega, defaults={"cantidad": valor_inicial}
    )
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
