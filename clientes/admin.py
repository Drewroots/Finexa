from django.contrib import admin

from .models import Tercero


@admin.register(Tercero)
class TerceroAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "numero_documento", "tipo", "empresa", "activo")
    list_filter = ("empresa", "tipo", "activo")
    search_fields = ("razon_social", "numero_documento")
