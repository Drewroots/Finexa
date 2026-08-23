# Finexa (NovaERP)

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
