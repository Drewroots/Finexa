# Arquitectura técnica — NovaERP (MVP)

## Stack

- **Lenguaje/Framework:** Python 3.12 + Django 5 (monolito modular, un solo lenguaje para todo: backend, lógica de negocio y frontend server-rendered).
- **Base de datos:** SQLite en desarrollo (`db.sqlite3`), migrable a PostgreSQL en producción con solo cambiar `DATABASES` en `novaerp/settings.py` — los modelos no usan nada específico de SQLite.
- **Frontend:** plantillas de Django + Bootstrap 5 (vía CDN) + un poco de JavaScript vanilla para el asistente. No requiere Node.js ni un build aparte.
- **Autenticación:** `django.contrib.auth` con modelo de usuario personalizado (`core.Usuario`), multi-tenant por `empresa_id`.
- **Admin:** `django.contrib.admin` queda disponible en `/admin/` para operaciones administrativas y soporte.

## Por qué monolito modular (no microservicios todavía)

El documento de planeación original propone microservicios a futuro. Para un MVP con 1 equipo pequeño, un monolito modular en Django:

- Reduce la complejidad operativa (un solo despliegue, una sola base de datos, transacciones ACID reales entre módulos — crítico para que facturación e inventario y contabilidad cuadren siempre).
- Cada módulo vive en su propia app de Django (`core`, `clientes`, `productos`, `contabilidad`, `facturacion`, `dashboard`), con límites claros de modelos/servicios/vistas, lo que facilita separarlo en un microservicio el día que el negocio lo justifique.

## Apps y responsabilidades

```
novaerp/          Configuración del proyecto (settings, urls raíz)
core/              Empresa (tenant), Usuario, autenticación, middleware multi-tenant
clientes/          Terceros (clientes/proveedores)
productos/         Productos/servicios, inventario y sus movimientos
contabilidad/      Plan de cuentas, libro diario, partida doble, balance
facturacion/       Facturas, ítems, emisión, pagos — orquesta inventario + contabilidad
dashboard/         KPIs agregados + asistente de negocio basado en reglas
```

## Multi-tenancy

Cada `Empresa` es un tenant lógico. Todas las tablas de negocio tienen `empresa` como FK obligatoria. El aislamiento se aplica en dos capas:

1. `core.middleware.EmpresaActualMiddleware` expone `request.empresa` en cada request autenticado.
2. `core.mixins.EmpresaQuerysetMixin` / `EmpresaFormMixin` fuerzan que toda vista basada en clases filtre y asigne por `request.empresa` — así ningún desarrollador puede "olvidarse" del filtro por tenant en una vista nueva.

Es el mismo patrón de aislamiento por `empresa_id` descrito en el documento de planeación original, listo para evolucionar a particionamiento por tenant si el volumen crece.

## Flujo de negocio central: factura → inventario → contabilidad

Este es el corazón del sistema y el que más valor de automatización aporta (ver HU-31 en `docs/HISTORIAS_USUARIO.md`):

1. `facturacion.services.crear_factura_borrador` crea la factura y sus ítems, calcula subtotal/IVA/total.
2. `facturacion.services.emitir_factura`:
   - Descuenta stock de cada producto vía `productos.services.registrar_movimiento` (atómico: mueve stock y deja rastro en `MovimientoInventario`).
   - Genera un asiento de partida doble vía `contabilidad.services.crear_transaccion`: débito a Clientes (CxC) por el total, crédito a Ingresos por ventas por el subtotal y crédito a IVA por pagar por el IVA.
   - Todo dentro de una única transacción de base de datos (`@transaction.atomic`): si algo falla, no queda inventario descontado sin su asiento, ni un asiento sin su factura.
3. `facturacion.services.registrar_pago` aplica un abono, genera el asiento de conciliación (débito a Caja/Bancos, crédito a Clientes) y marca la factura como Pagada cuando el saldo llega a cero.

`contabilidad.services.crear_transaccion` valida que todo asiento cuadre (`total_débitos == total_créditos`) antes de guardarlo — es la regla de integridad contable más importante del sistema y está centralizada en un solo lugar para que ningún módulo pueda generar un asiento descuadrado.

## Seguridad

- Contraseñas con el hasher por defecto de Django (PBKDF2).
- CSRF activado en todos los formularios y en la llamada AJAX del asistente.
- Toda vista de negocio requiere `login_required` / `LoginRequiredMixin`.
- Aislamiento multi-tenant descrito arriba evita fugas de datos entre empresas.
- Pendiente antes de producción real: forzar HTTPS, rotar `SECRET_KEY` por variable de entorno (ya soportado vía `NOVAERP_SECRET_KEY`), y 2FA (ver HU-06).

## Cómo evolucionar hacia la arquitectura de escala (fase futura)

Cuando el volumen lo justifique, cada app Django puede convertirse en un servicio independiente sin rediseñar el modelo de datos, porque los límites ya existen:

- `contabilidad` y `facturacion` seguirían siendo el núcleo transaccional (PostgreSQL).
- Se añadiría Redis para colas (envío de documentos DIAN, WhatsApp, recordatorios de cobro) y caché de KPIs.
- El asistente de negocio (`dashboard.services.asistente_responder`) es hoy reglas simples; el punto de extensión para conectar un LLM real (fase 6 del roadmap) es esa misma función.
