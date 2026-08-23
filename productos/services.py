from django.db import transaction

from .models import MovimientoInventario


@transaction.atomic
def registrar_movimiento(producto, tipo, cantidad, usuario=None, motivo="", referencia=""):
    """Crea un MovimientoInventario y ajusta el stock_actual del producto de forma atómica."""
    if tipo == "SALIDA":
        producto.stock_actual -= cantidad
    else:
        producto.stock_actual += cantidad
    producto.save(update_fields=["stock_actual"])

    return MovimientoInventario.objects.create(
        empresa=producto.empresa,
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo,
        referencia=referencia,
        usuario=usuario,
    )
