from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import Empresa

from .services import CUENTA_CLIENTES, CUENTA_INGRESOS_VENTAS, crear_transaccion, sembrar_plan_cuentas


class PlanCuentasTests(TestCase):
    def test_sembrar_plan_cuentas_es_idempotente(self):
        empresa = Empresa.objects.create(nombre="Acme", nit="900000001-1")
        sembrar_plan_cuentas(empresa)
        total_inicial = empresa.cuentas.count()

        sembrar_plan_cuentas(empresa)  # segunda llamada no debe duplicar cuentas

        self.assertEqual(empresa.cuentas.count(), total_inicial)
        self.assertGreater(total_inicial, 0)


class CrearTransaccionTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre="Acme", nit="900000002-1")
        sembrar_plan_cuentas(self.empresa)

    def test_asiento_balanceado_se_crea_correctamente(self):
        transaccion = crear_transaccion(
            empresa=self.empresa,
            fecha=timezone.localdate(),
            descripcion="Venta de prueba",
            lineas=[
                (CUENTA_CLIENTES, Decimal("100"), Decimal("0")),
                (CUENTA_INGRESOS_VENTAS, Decimal("0"), Decimal("100")),
            ],
        )
        self.assertTrue(transaccion.cuadrada)
        self.assertEqual(transaccion.total_debitos, Decimal("100"))
        self.assertEqual(transaccion.total_creditos, Decimal("100"))

    def test_asiento_descuadrado_lanza_error_y_no_se_guarda(self):
        with self.assertRaises(ValidationError):
            crear_transaccion(
                empresa=self.empresa,
                fecha=timezone.localdate(),
                descripcion="Asiento inválido",
                lineas=[
                    (CUENTA_CLIENTES, Decimal("100"), Decimal("0")),
                    (CUENTA_INGRESOS_VENTAS, Decimal("0"), Decimal("50")),
                ],
            )
        self.assertEqual(self.empresa.transacciones.count(), 0)
