from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from contabilidad.services import (
    CUENTA_CLIENTES,
    CUENTA_IVA_POR_PAGAR,
    CUENTA_INGRESOS_VENTAS,
    crear_transaccion,
)
from productos.services import registrar_movimiento

from .models import Factura, FacturaItem, NotaCreditoDebito

MAX_INTENTOS_NUMERACION = 5


def asignar_numero_factura(factura):
    """Asigna y guarda un número de factura consecutivo por empresa.

    `factura` debe ser una instancia sin guardar (numero aún sin asignar). El número
    consecutivo se calcula con MAX(numero)+1, lo que es vulnerable a condiciones de
    carrera si dos facturas se crean al mismo tiempo para la misma empresa; por eso
    reintentamos ante el IntegrityError de la restricción unique_together en vez de
    dejar que se propague como error 500.
    """
    for _ in range(MAX_INTENTOS_NUMERACION):
        ultimo_numero = Factura.objects.filter(empresa=factura.empresa).order_by("-numero").values_list(
            "numero", flat=True
        ).first() or 0
        factura.numero = ultimo_numero + 1
        try:
            with transaction.atomic():
                factura.save()
            return factura
        except IntegrityError:
            continue
    raise ValidationError("No se pudo asignar un número de factura, intenta de nuevo.")


@transaction.atomic
def crear_factura_borrador(empresa, cliente, fecha_emision, fecha_vencimiento, items, usuario=None, notas=""):
    """Crea una factura en estado BORRADOR con sus ítems.

    `items` es una lista de dicts: {"producto": Producto, "cantidad": Decimal, "precio_unitario": Decimal}
    """
    factura = Factura(
        empresa=empresa,
        cliente=cliente,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        usuario=usuario,
        notas=notas,
    )
    asignar_numero_factura(factura)

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


@transaction.atomic
def crear_nota_credito_debito(factura, tipo, valor, motivo, usuario=None, fecha=None):
    """Emite una nota credito/debito sobre una factura ya emitida (HU-21).

    Simplificacion: `valor` se trata como un monto total (sin desglose de IVA
    propio) que ajusta directamente Ingresos y Cuentas por cobrar. Suficiente
    para el MVP; un desglose formal de IVA en la nota queda para una iteracion
    posterior si se requiere.
    """
    from django.utils import timezone

    if factura.estado not in ("EMITIDA", "PAGADA"):
        raise ValidationError("Solo se pueden emitir notas sobre facturas emitidas.")
    if valor <= 0:
        raise ValidationError("El valor de la nota debe ser mayor a cero.")
    if tipo == "CREDITO" and valor > factura.total:
        raise ValidationError("La nota crédito no puede superar el total de la factura.")

    fecha = fecha or timezone.localdate()

    if tipo == "CREDITO":
        lineas = [
            (CUENTA_INGRESOS_VENTAS, valor, Decimal("0")),
            (CUENTA_CLIENTES, Decimal("0"), valor),
        ]
    else:
        lineas = [
            (CUENTA_CLIENTES, valor, Decimal("0")),
            (CUENTA_INGRESOS_VENTAS, Decimal("0"), valor),
        ]

    transaccion = crear_transaccion(
        empresa=factura.empresa,
        fecha=fecha,
        descripcion=f"Nota {tipo.lower()} sobre factura #{factura.numero:05d}: {motivo}",
        lineas=lineas,
        documento_origen=f"Factura #{factura.numero:05d}",
        usuario=usuario,
    )

    nota = None
    for _ in range(MAX_INTENTOS_NUMERACION):
        ultimo_numero = NotaCreditoDebito.objects.filter(empresa=factura.empresa).order_by("-numero").values_list(
            "numero", flat=True
        ).first() or 0
        try:
            with transaction.atomic():
                nota = NotaCreditoDebito.objects.create(
                    empresa=factura.empresa,
                    factura=factura,
                    numero=ultimo_numero + 1,
                    tipo=tipo,
                    valor=valor,
                    motivo=motivo,
                    fecha=fecha,
                    usuario=usuario,
                    transaccion=transaccion,
                )
            break
        except IntegrityError:
            continue
    if nota is None:
        raise ValidationError("No se pudo asignar un número de nota, intenta de nuevo.")

    if tipo == "CREDITO":
        factura.total -= valor
        factura.saldo_pendiente = max(factura.saldo_pendiente - valor, Decimal("0"))
    else:
        factura.total += valor
        factura.saldo_pendiente += valor

    if factura.saldo_pendiente <= 0 and factura.estado == "EMITIDA":
        factura.estado = "PAGADA"
    elif factura.saldo_pendiente > 0 and factura.estado == "PAGADA":
        factura.estado = "EMITIDA"
    factura.save(update_fields=["total", "saldo_pendiente", "estado"])

    return nota
