from django.contrib import admin

from .models import MovimientoInventario, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "precio_venta", "stock_actual", "empresa")
    list_filter = ("empresa", "tipo", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "fecha", "empresa")
    list_filter = ("empresa", "tipo")
