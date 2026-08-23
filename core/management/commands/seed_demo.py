from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from clientes.models import Tercero
from contabilidad.services import sembrar_plan_cuentas
from core.models import Empresa, Usuario
from facturacion.services import crear_factura_borrador, emitir_factura, registrar_pago
from productos.models import Producto


class Command(BaseCommand):
    help = "Crea una empresa demo con usuario, clientes, productos y una factura de ejemplo."

    def handle(self, *args, **options):
        if Empresa.objects.filter(nit="900123456-1").exists():
            self.stdout.write(self.style.WARNING("La empresa demo ya existe. No se creó nada."))
            return

        empresa = Empresa.objects.create(
            nombre="Panadería La Espiga Demo",
            nit="900123456-1",
            email="demo@novaerp.local",
        )
        sembrar_plan_cuentas(empresa)

        usuario = Usuario.objects.create_user(
            username="demo",
            password="novaerp2026",
            email="demo@novaerp.local",
            first_name="Usuario",
            last_name="Demo",
            empresa=empresa,
            rol=Usuario.ROL_DUENIO,
        )

        cliente = Tercero.objects.create(
            empresa=empresa,
            tipo_documento="CC",
            numero_documento="1010101010",
            tipo="CLIENTE",
            razon_social="Cliente de Prueba",
            email="cliente@demo.local",
        )

        pan = Producto.objects.create(
            empresa=empresa,
            codigo="PAN-001",
            nombre="Pan francés (unidad)",
            tipo="PRODUCTO",
            precio_venta=Decimal("1500"),
            costo=Decimal("700"),
            porcentaje_iva=Decimal("0"),
            unidad_medida="UND",
            stock_actual=Decimal("200"),
            stock_minimo=Decimal("50"),
        )
        torta = Producto.objects.create(
            empresa=empresa,
            codigo="TOR-010",
            nombre="Torta de chocolate",
            tipo="PRODUCTO",
            precio_venta=Decimal("65000"),
            costo=Decimal("30000"),
            porcentaje_iva=Decimal("19"),
            unidad_medida="UND",
            stock_actual=Decimal("5"),
            stock_minimo=Decimal("3"),
        )

        hoy = timezone.localdate()
        factura = crear_factura_borrador(
            empresa=empresa,
            cliente=cliente,
            fecha_emision=hoy,
            fecha_vencimiento=hoy + timedelta(days=30),
            items=[
                {"producto": pan, "cantidad": Decimal("20"), "precio_unitario": pan.precio_venta},
                {"producto": torta, "cantidad": Decimal("1"), "precio_unitario": torta.precio_venta},
            ],
            usuario=usuario,
        )
        emitir_factura(factura, usuario=usuario)
        registrar_pago(factura, monto=Decimal("30000"), cuenta_destino_codigo="1105", usuario=usuario)

        self.stdout.write(self.style.SUCCESS("Empresa demo creada."))
        self.stdout.write("Usuario: demo / Contraseña: novaerp2026")
