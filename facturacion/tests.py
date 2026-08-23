from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from clientes.models import Tercero
from contabilidad.services import sembrar_plan_cuentas
from core.models import Empresa
from productos.models import Producto

from .services import crear_factura_borrador, emitir_factura, registrar_pago


class FacturacionFlowTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Panadería Test", nit="900000003-1")
        sembrar_plan_cuentas(self.empresa)
        self.cliente = Tercero.objects.create(
            empresa=self.empresa,
            numero_documento="123",
            razon_social="Cliente Test",
        )
        self.producto = Producto.objects.create(
            empresa=self.empresa,
            codigo="P1",
            nombre="Producto Test",
            precio_venta=Decimal("1000"),
            porcentaje_iva=Decimal("19"),
            stock_actual=Decimal("50"),
            stock_minimo=Decimal("10"),
        )

    def _crear_factura(self, cantidad=Decimal("5")):
        hoy = timezone.localdate()
        return crear_factura_borrador(
            empresa=self.empresa,
            cliente=self.cliente,
            fecha_emision=hoy,
            fecha_vencimiento=hoy,
            items=[{"producto": self.producto, "cantidad": cantidad, "precio_unitario": self.producto.precio_venta}],
        )

    def test_totales_de_factura_incluyen_iva(self):
        factura = self._crear_factura(cantidad=Decimal("5"))
        # 5 * 1000 = 5000 subtotal, 19% IVA = 950
        self.assertEqual(factura.subtotal, Decimal("5000"))
        self.assertEqual(factura.iva, Decimal("950"))
        self.assertEqual(factura.total, Decimal("5950"))
        self.assertEqual(factura.estado, "BORRADOR")

    def test_emitir_factura_descuenta_stock_y_genera_asiento_balanceado(self):
        factura = self._crear_factura(cantidad=Decimal("5"))
        stock_inicial = self.producto.stock_actual

        emitir_factura(factura)

        self.producto.refresh_from_db()
        factura.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, stock_inicial - Decimal("5"))
        self.assertEqual(factura.estado, "EMITIDA")

        transaccion = self.empresa.transacciones.get()
        self.assertTrue(transaccion.cuadrada)
        self.assertEqual(transaccion.total_debitos, factura.total)

    def test_no_se_puede_emitir_una_factura_ya_emitida(self):
        factura = self._crear_factura()
        emitir_factura(factura)
        with self.assertRaises(ValidationError):
            emitir_factura(factura)

    def test_registrar_pago_marca_factura_como_pagada_al_saldar(self):
        factura = self._crear_factura()
        emitir_factura(factura)

        registrar_pago(factura, monto=factura.total, cuenta_destino_codigo="1105")

        factura.refresh_from_db()
        self.assertEqual(factura.saldo_pendiente, Decimal("0"))
        self.assertEqual(factura.estado, "PAGADA")

    def test_registrar_pago_no_permite_exceder_el_saldo(self):
        factura = self._crear_factura()
        emitir_factura(factura)
        with self.assertRaises(ValidationError):
            registrar_pago(factura, monto=factura.total + Decimal("1"), cuenta_destino_codigo="1105")
