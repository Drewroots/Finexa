from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Empresa, Usuario


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "regimen", "creado_en")
    search_fields = ("nombre", "nit")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("NovaERP", {"fields": ("empresa", "rol", "telefono")}),
    )
    list_display = ("username", "email", "empresa", "rol", "is_staff")
    list_filter = ("empresa", "rol", "is_staff")
