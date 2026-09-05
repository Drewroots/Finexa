from django.contrib import admin

from .models import CuentaContable, MovimientoBancario, MovimientoContable, TareaCierre, Transaccion


@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "naturaleza", "empresa", "activa")
    list_filter = ("empresa", "tipo")


class MovimientoInline(admin.TabularInline):
    model = MovimientoContable
    extra = 0


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "descripcion", "documento_origen", "empresa")
    list_filter = ("empresa",)
    inlines = [MovimientoInline]


@admin.register(TareaCierre)
class TareaCierreAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "anio", "mes", "completada", "empresa")
    list_filter = ("empresa", "anio", "mes", "completada")


@admin.register(MovimientoBancario)
class MovimientoBancarioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "descripcion", "valor", "conciliado", "empresa")
    list_filter = ("empresa", "conciliado")
