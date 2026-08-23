from django.contrib.auth.models import AbstractUser
from django.db import models


class Empresa(models.Model):
    """Tenant: cada empresa es un cliente de NovaERP con sus datos aislados."""

    REGIMEN_CHOICES = [
        ("SIMPLE", "Régimen Simple de Tributación"),
        ("ORDINARIO", "Régimen Ordinario"),
        ("NO_RESPONSABLE_IVA", "No responsable de IVA"),
    ]

    nombre = models.CharField("Razón social", max_length=200)
    nit = models.CharField("NIT", max_length=20, unique=True)
    regimen = models.CharField(max_length=30, choices=REGIMEN_CHOICES, default="ORDINARIO")
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.nit})"


class Usuario(AbstractUser):
    """Usuario del sistema, asociado a una empresa (tenant) y a un rol funcional."""

    ROL_DUENIO = "DUENIO"
    ROL_CONTADOR = "CONTADOR"
    ROL_VENDEDOR = "VENDEDOR"
    ROL_CHOICES = [
        (ROL_DUENIO, "Dueño / Administrador"),
        (ROL_CONTADOR, "Contador"),
        (ROL_VENDEDOR, "Vendedor"),
    ]

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="usuarios", null=True, blank=True
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_VENDEDOR)
    telefono = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_duenio(self):
        return self.rol == self.ROL_DUENIO

    @property
    def es_contador(self):
        return self.rol == self.ROL_CONTADOR
