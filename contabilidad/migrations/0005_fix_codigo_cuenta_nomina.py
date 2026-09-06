from django.db import migrations

# El codigo "2365" del Decreto 2650 (PUC) es oficialmente "Retencion en la
# fuente", no "Retenciones y aportes de nomina" (ese es el "2370"). Este dato
# se sembro con el codigo equivocado desde el inicio del proyecto; aqui se
# corrige in-place la cuenta ya creada en empresas existentes -- se actualiza
# el codigo/nombre de la fila, no se crea una cuenta nueva, asi que los
# asientos ya contabilizados contra ella (via su FK por id) quedan intactos.

NOMBRE_VIEJO = "Retenciones y aportes de nómina por pagar"
NOMBRE_NUEVO = "Retenciones y aportes de nómina"


def corregir_codigo(apps, schema_editor):
    CuentaContable = apps.get_model("contabilidad", "CuentaContable")
    CuentaContable.objects.filter(codigo="2365", nombre=NOMBRE_VIEJO).update(
        codigo="2370", nombre=NOMBRE_NUEVO
    )


def revertir(apps, schema_editor):
    CuentaContable = apps.get_model("contabilidad", "CuentaContable")
    CuentaContable.objects.filter(codigo="2370", nombre=NOMBRE_NUEVO).update(
        codigo="2365", nombre=NOMBRE_VIEJO
    )


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidad", "0004_movimientobancario"),
    ]

    operations = [
        migrations.RunPython(corregir_codigo, revertir),
    ]
