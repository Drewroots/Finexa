from django.contrib import admin

from .models import Factura, FacturaItem


class FacturaItemInline(admin.TabularInline):
    model = FacturaItem
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "estado", "total", "saldo_pendiente", "empresa")
    list_filter = ("empresa", "estado")
    search_fields = ("numero",)
    inlines = [FacturaItemInline]
