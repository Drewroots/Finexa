from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from contabilidad.services import (
    CUENTA_CLIENTES,
    CUENTA_IVA_POR_PAGAR,
    CUENTA_INGRESOS_VENTAS,
    crear_transaccion,
)
from productos.services import registrar_movimiento

from .models import Factura, FacturaItem


@transaction.atomic
def crear_factura_borrador(empresa, cliente, fecha_emision, fecha_vencimiento, items, usuario=None, notas=""):
    """Crea una factura en estado BORRADOR con sus ítems.

    `items` es una lista de dicts: {"producto": Producto, "cantidad": Decimal, "precio_unitario": Decimal}
    """
    ultimo_numero = Factura.objects.filter(empresa=empresa).order_by("-numero").values_list(
        "numero", flat=True
    ).first() or 0

    factura = Factura.objects.create(
        empresa=empresa,
        numero=ultimo_numero + 1,
        cliente=cliente,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        usuario=usuario,
        notas=notas,
    )

    for item in items:
        FacturaItem.objects.create(
            factura=factura,
            producto=item["producto"],
            cantidad=item["cantidad"],
            precio_unitario=item["precio_unitario"],
            porcentaje_iva=item.get("porcentaje_iva", item["producto"].porcentaje_iva),
        )

    recalcular_totales(factura)
    return factura


def recalcular_totales(factura):
    items = list(factura.items.all())
    subtotal = sum((i.subtotal for i in items), Decimal("0"))
    iva = sum((i.valor_iva for i in items), Decimal("0"))
    factura.subtotal = subtotal
    factura.iva = iva
    factura.total = subtotal + iva
    factura.saldo_pendiente = factura.total
    factura.save(update_fields=["subtotal", "iva", "total", "saldo_pendiente"])


@transaction.atomic
def emitir_factura(factura, usuario=None):
    """Emite una factura BORRADOR: descuenta inventario y genera el asiento contable."""
    if factura.estado != "BORRADOR":
        raise ValidationError("Solo se pueden emitir facturas en estado borrador.")
    if not factura.items.exists():
        raise ValidationError("La factura no tiene ítems.")

    for item in factura.items.select_related("producto"):
        if item.producto.tipo == "PRODUCTO":
            registrar_movimiento(
                producto=item.producto,
                tipo="SALIDA",
                cantidad=item.cantidad,
                usuario=usuario,
                motivo="Venta",
                referencia=f"Factura #{factura.numero:05d}",
            )

    lineas = [
        (CUENTA_CLIENTES, factura.total, Decimal("0")),
        (CUENTA_INGRESOS_VENTAS, Decimal("0"), factura.subtotal),
    ]
    if factura.iva:
        lineas.append((CUENTA_IVA_POR_PAGAR, Decimal("0"), factura.iva))

    crear_transaccion(
        empresa=factura.empresa,
        fecha=factura.fecha_emision,
        descripcion=f"Venta según factura #{factura.numero:05d} a {factura.cliente.razon_social}",
        lineas=lineas,
        documento_origen=f"Factura #{factura.numero:05d}",
        usuario=usuario,
    )

    factura.estado = "EMITIDA"
    factura.save(update_fields=["estado"])
    return factura


@transaction.atomic
def registrar_pago(factura, monto, cuenta_destino_codigo, usuario=None, fecha=None):
    """Aplica un abono/pago a una factura emitida y genera el asiento de conciliación."""
    from django.utils import timezone

    from contabilidad.services import crear_transaccion

    if factura.estado not in ("EMITIDA", "PAGADA"):
        raise ValidationError("Solo se pueden registrar pagos sobre facturas emitidas.")
    if monto <= 0 or monto > factura.saldo_pendiente:
        raise ValidationError("El monto del pago no es válido.")

    fecha = fecha or timezone.localdate()

    crear_transaccion(
        empresa=factura.empresa,
        fecha=fecha,
        descripcion=f"Pago recibido factura #{factura.numero:05d}",
        lineas=[
            (cuenta_destino_codigo, monto, Decimal("0")),
            (CUENTA_CLIENTES, Decimal("0"), monto),
        ],
        documento_origen=f"Factura #{factura.numero:05d}",
        usuario=usuario,
    )

    factura.saldo_pendiente -= monto
    if factura.saldo_pendiente <= 0:
        factura.estado = "PAGADA"
        factura.saldo_pendiente = Decimal("0")
    factura.save(update_fields=["saldo_pendiente", "estado"])
    return factura
