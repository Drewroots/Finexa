# Finexa (NovaERP)

[![CI](https://github.com/Drewroots/Finexa/actions/workflows/ci.yml/badge.svg)](https://github.com/Drewroots/Finexa/actions/workflows/ci.yml)

Finexa — Modern ERP for Colombian SMEs. Accounting, DIAN invoicing, inventory, payroll, and AI insights in one integrated platform.

MVP construido en **Python + Django**: login multi-tenant, base de datos, facturación con generación automática de asientos contables, inventario e panel de decisión con KPIs y un asistente de negocio.

Documentación:

- [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) — cómo está estructurado el proyecto y por qué.
- [`docs/HISTORIAS_USUARIO.md`](docs/HISTORIAS_USUARIO.md) — historias de usuario por módulo, con estado (hecho/pendiente).
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — avance por fase y próximos pasos.

## Requisitos

- Python 3.11+

## Instalación

```bash
python -m venv .venv
.venv/Scripts/activate       # Windows
source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
```

## Ejecutar en desarrollo

```bash
python manage.py runserver
```

Abre http://127.0.0.1:8000 — te redirige al login. Puedes registrar una empresa nueva desde ahí, o cargar datos de ejemplo:

```bash
python manage.py seed_demo
```

Esto crea la empresa demo **"Panadería La Espiga Demo"** con usuario `demo` / contraseña `novaerp2026`, ya con clientes, productos, una factura emitida y un pago registrado, para explorar el sistema sin capturar datos a mano.

## Panel de administración

```bash
python manage.py createsuperuser
```

Luego entra a `/admin/` para gestionar cualquier dato directamente.

## Pruebas y CI

```bash
python manage.py test
```

Cada push y pull request a `main` corre automáticamente en GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): `manage.py check`, verificación de migraciones faltantes y la suite de pruebas, en Python 3.11 y 3.12.

## Contribuir

- Los pull requests siguen la plantilla en [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).
- Los issues tienen plantillas para bugs y nuevas funcionalidades en [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).
- Dependabot revisa semanalmente actualizaciones de dependencias de pip y de las GitHub Actions.
