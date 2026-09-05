from django.contrib import admin

from .models import Factura, FacturaItem, NotaCreditoDebito


class FacturaItemInline(admin.TabularInline):
    model = FacturaItem
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "estado", "total", "saldo_pendiente", "empresa")
    list_filter = ("empresa", "estado")
    search_fields = ("numero",)
    inlines = [FacturaItemInline]


@admin.register(NotaCreditoDebito)
class NotaCreditoDebitoAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "factura", "valor", "fecha", "empresa")
    list_filter = ("empresa", "tipo")
    search_fields = ("numero",)
