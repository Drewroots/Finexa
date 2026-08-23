from django.test import TestCase

from .forms import RegistroEmpresaForm
from .models import Usuario


class RegistroEmpresaFormTests(TestCase):
    def test_registro_crea_empresa_usuario_dueno_y_plan_de_cuentas(self):
        form = RegistroEmpresaForm(
            data={
                "empresa_nombre": "Acme SAS",
                "empresa_nit": "900123456-1",
                "email": "acme@example.com",
                "username": "acmeowner",
                "password1": "una-clave-segura-123",
                "password2": "una-clave-segura-123",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        usuario = form.save()

        self.assertEqual(usuario.rol, Usuario.ROL_DUENIO)
        self.assertIsNotNone(usuario.empresa)
        self.assertEqual(usuario.empresa.nombre, "Acme SAS")
        self.assertGreater(usuario.empresa.cuentas.count(), 0)
