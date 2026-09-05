from django.db import migrations


def crear_bodega_principal_y_migrar_stock(apps, schema_editor):
    Empresa = apps.get_model("core", "Empresa")
    Bodega = apps.get_model("productos", "Bodega")
    Producto = apps.get_model("productos", "Producto")
    StockPorBodega = apps.get_model("productos", "StockPorBodega")
    MovimientoInventario = apps.get_model("productos", "MovimientoInventario")

    for empresa in Empresa.objects.all():
        bodega, _ = Bodega.objects.get_or_create(empresa=empresa, nombre="Principal")

        for producto in Producto.objects.filter(empresa=empresa):
            StockPorBodega.objects.get_or_create(
                producto=producto, bodega=bodega, defaults={"cantidad": producto.stock_actual}
            )

        MovimientoInventario.objects.filter(empresa=empresa, bodega__isnull=True).update(bodega=bodega)


def revertir(apps, schema_editor):
    # No es necesario deshacer: eliminar las bodegas "Principal" perderia
    # trazabilidad del stock existente sin ningun beneficio.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0002_bodega_movimientoinventario_bodega_stockporbodega"),
    ]

    operations = [
        migrations.RunPython(crear_bodega_principal_y_migrar_stock, revertir),
    ]
