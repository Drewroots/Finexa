from django.contrib import admin

from .models import Bodega, MovimientoInventario, Producto, StockPorBodega


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "precio_venta", "stock_actual", "empresa")
    list_filter = ("empresa", "tipo", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "bodega", "tipo", "cantidad", "fecha", "empresa")
    list_filter = ("empresa", "tipo", "bodega")


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "activa")
    list_filter = ("empresa", "activa")


@admin.register(StockPorBodega)
class StockPorBodegaAdmin(admin.ModelAdmin):
    list_display = ("producto", "bodega", "cantidad")
    list_filter = ("bodega",)
