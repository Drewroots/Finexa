from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from clientes.models import Tercero
from contabilidad.services import sembrar_plan_cuentas
from core.models import Empresa
from facturacion.services import crear_factura_borrador, emitir_factura
from productos.models import Producto

from .services import asistente_responder, calcular_kpis


class DashboardKpiTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Tienda Test", nit="900000004-1")
        sembrar_plan_cuentas(self.empresa)
        cliente = Tercero.objects.create(empresa=self.empresa, numero_documento="1", razon_social="Cliente")
        self.producto = Producto.objects.create(
            empresa=self.empresa,
            codigo="P1",
            nombre="Producto bajo stock",
            precio_venta=Decimal("2000"),
            porcentaje_iva=Decimal("0"),
            stock_actual=Decimal("2"),
            stock_minimo=Decimal("5"),
        )
        hoy = timezone.localdate()
        factura = crear_factura_borrador(
            empresa=self.empresa,
            cliente=cliente,
            fecha_emision=hoy,
            fecha_vencimiento=hoy,
            items=[{"producto": self.producto, "cantidad": Decimal("1"), "precio_unitario": Decimal("2000")}],
        )
        emitir_factura(factura)

    def test_calcular_kpis_refleja_ventas_cartera_y_stock_bajo(self):
        kpis = calcular_kpis(self.empresa)

        self.assertEqual(kpis["ventas_mes"], Decimal("2000"))
        self.assertEqual(kpis["cuentas_por_cobrar"], Decimal("2000"))
        self.assertIn(self.producto, kpis["productos_bajo_stock"])

    def test_asistente_responde_sobre_cartera(self):
        respuesta = asistente_responder(self.empresa, "¿cuánto tengo por cobrar?")
        self.assertIn("2,000", respuesta.replace("$", ""))

    def test_asistente_responde_mensaje_por_defecto_si_no_entiende(self):
        respuesta = asistente_responder(self.empresa, "cuéntame un chiste")
        self.assertIn("Puedo responder sobre", respuesta)
