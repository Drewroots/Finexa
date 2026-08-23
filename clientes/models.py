from django.db import models

from core.models import Empresa


class Tercero(models.Model):
    """Cliente y/o proveedor de la empresa (tenant)."""

    TIPO_DOC_CHOICES = [
        ("CC", "Cédula de ciudadanía"),
        ("NIT", "NIT"),
        ("CE", "Cédula de extranjería"),
        ("PAS", "Pasaporte"),
    ]
    TIPO_TERCERO_CHOICES = [
        ("CLIENTE", "Cliente"),
        ("PROVEEDOR", "Proveedor"),
        ("AMBOS", "Cliente y proveedor"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="terceros")
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOC_CHOICES, default="CC")
    numero_documento = models.CharField(max_length=20)
    tipo = models.CharField(max_length=10, choices=TIPO_TERCERO_CHOICES, default="CLIENTE")
    razon_social = models.CharField("Nombre / razón social", max_length=200)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tercero"
        verbose_name_plural = "Terceros"
        ordering = ["razon_social"]
        unique_together = ("empresa", "numero_documento")

    def __str__(self):
        return f"{self.razon_social} ({self.numero_documento})"

    @property
    def es_cliente(self):
        return self.tipo in ("CLIENTE", "AMBOS")

    @property
    def es_proveedor(self):
        return self.tipo in ("PROVEEDOR", "AMBOS")
