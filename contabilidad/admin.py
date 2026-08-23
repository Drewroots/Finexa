from django.contrib import admin

from .models import CuentaContable, MovimientoContable, Transaccion


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
