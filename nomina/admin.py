from django.contrib import admin

from .models import Empleado, Liquidacion


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "numero_documento", "cargo", "salario_base", "activo", "empresa")
    list_filter = ("empresa", "activo")
    search_fields = ("nombre_completo", "numero_documento")


@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "anio", "mes", "total_devengado", "neto_pagado", "empresa")
    list_filter = ("empresa", "anio", "mes")
