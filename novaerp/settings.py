"""
Configuración de Django para NovaERP.
"""

from decimal import Decimal
from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("NOVAERP_DEBUG", "True") == "True"

SECRET_KEY = os.environ.get("NOVAERP_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Define la variable de entorno NOVAERP_SECRET_KEY cuando NOVAERP_DEBUG=False."
        )
    # Clave insegura solo para desarrollo local (NOVAERP_DEBUG=True).
    SECRET_KEY = "django-insecure-xcm2z-7k6k0gp#+b3emud!8g&6kq@#r#d2dbw%hke_3!w%fcbo"

ALLOWED_HOSTS = os.environ.get("NOVAERP_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps de NovaERP (dominio funcional)
    'core',
    'clientes',
    'productos',
    'contabilidad',
    'facturacion',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.EmpresaActualMiddleware',
]

ROOT_URLCONF = 'novaerp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'novaerp.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'core.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'core:login'

# Email: por defecto imprime los correos en consola (dev). En producción,
# define NOVAERP_EMAIL_HOST (y el resto de NOVAERP_EMAIL_*) para usar SMTP real.
if os.environ.get("NOVAERP_EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ["NOVAERP_EMAIL_HOST"]
    EMAIL_PORT = int(os.environ.get("NOVAERP_EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("NOVAERP_EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("NOVAERP_EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.environ.get("NOVAERP_EMAIL_USE_TLS", "True") == "True"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("NOVAERP_DEFAULT_FROM_EMAIL", "no-responder@novaerp.local")

# Nomina: valores de referencia 2026 (COP). Ajustar cada ano segun decreto del
# Gobierno colombiano; ver contabilidad de nomina en docs/HISTORIAS_USUARIO.md HU-28.
SALARIO_MINIMO_LEGAL = Decimal("1423500")
AUXILIO_TRANSPORTE = Decimal("200000")
