# Roadmap y avance — NovaERP

Última actualización: 2026-09-05.

## Resumen de avance por fase

| Fase | Alcance original | Estado | Detalle |
|---|---|---|---|
| 1. Fundamentos | Autenticación, multi-tenant, modelo de datos base | ✅ **Hecho** | Login (con 2FA opcional por TOTP), recuperación de contraseña por correo, registro de empresa, roles (Dueño/Contador/Vendedor), aislamiento por tenant. |
| 2. Facturación + Contabilidad básica | MVP facturable con reportes contables mínimos | ✅ **Hecho** | Facturación con ítems, emisión con asiento automático de partida doble, notas crédito/débito, libro diario, balance de comprobación, balance general y estado de resultados formales, checklist de cierre mensual, conciliación bancaria (carga de extracto CSV). |
| 3. Inventario + POS | Módulo de ventas físicas integrado | 🚧 **Parcial** | Inventario multi-producto y multi-bodega, con descuento automático y alertas de stock mínimo. **Falta:** POS offline-first, código de barras. |
| 4. Cuentas por cobrar/pagar + flujo de caja | Automatización de cobros y proyecciones | 🚧 **Parcial** | CxC con saldo por factura, registro de pagos, notas crédito/débito, flujo de caja proyectado a 30/60/90 días, conciliación bancaria por extracto. **Falta:** recordatorios automáticos por WhatsApp/email, módulo de cuentas por pagar a proveedores. |
| 5. Nómina electrónica | Cumplimiento DIAN nómina | 🚧 **Parcial** | Liquidación de nómina (salud, pensión, ARL, caja de compensación, cesantías, prima, vacaciones) con asiento contable. **Falta:** documento electrónico de nómina ante la DIAN (requiere un Proveedor Tecnológico Autorizado). |
| 6. IA y dashboard | Asistente conversacional + KPIs | 🚧 **Parcial** | Dashboard con KPIs reales (ventas, cartera, IVA por pagar, stock bajo, flujo proyectado) y un asistente de preguntas frecuentes basado en reglas (no LLM todavía). |

Ver `docs/HISTORIAS_USUARIO.md` para el detalle historia por historia con criterios de aceptación.

## Qué se puede hacer hoy con el MVP

1. Registrar una empresa nueva (`/registro/`) — crea automáticamente el plan de cuentas base.
2. Invitar usuarios con rol Contador o Vendedor (`/equipo/`, solo visible para el Dueño).
3. Registrar clientes y proveedores (`/clientes/`).
4. Registrar productos/servicios con precio, costo, IVA y stock (`/productos/`).
5. Crear una factura con varios ítems, emitirla (descuenta inventario + genera asiento contable) y registrar pagos parciales o totales (`/facturas/`).
6. Consultar el libro diario y el balance de comprobación (`/contabilidad/`).
7. Ver el panel de decisión con KPIs en tiempo real y preguntarle al asistente cosas como *"¿cuánto debo en impuestos este mes?"* (`/dashboard/`).

Para ver todo esto ya poblado con datos de ejemplo:

```bash
python manage.py seed_demo
```

Crea la empresa demo "Panadería La Espiga Demo" con usuario `demo` / contraseña `novaerp2026`.

## Próximos pasos sugeridos (en orden de impacto)

1. **Cuentas por pagar a proveedores** — hoy solo existe CxC de clientes; falta el flujo espejo de compras/gastos.
2. **Integración DIAN real** vía un Proveedor Tecnológico Autorizado — es el riesgo más crítico señalado en el documento de planeación original y debe validarse externamente antes de cualquier lanzamiento comercial (HU-19, HU-29).
3. **Asistente con LLM real** conectado a los mismos KPIs que ya calcula `dashboard.services.calcular_kpis`, reemplazando las reglas por un modelo de lenguaje con contexto del negocio (HU-33). Necesita que el negocio aporte una API key de un proveedor de LLM.
4. **Envío automático de factura por WhatsApp** (HU-20) — el envío por email ya podría añadirse fácilmente sobre `django.core.mail`; la parte de WhatsApp necesita una cuenta de WhatsApp Business API verificada.
5. **POS offline-first** para ventas físicas (React Native + SQLite local, como en el plan original) — hoy la facturación asume conexión permanente.

Hechos en esta iteración (antes pendientes): recuperación de contraseña y 2FA (HU-05, HU-06), stock por bodega (HU-14), notas crédito/débito (HU-21), balance general y estado de resultados (HU-25), checklist de cierre (HU-26), conciliación bancaria simplificada por CSV (HU-27), y liquidación de nómina (HU-28).

## Riesgos vigentes (heredados del documento de planeación)

- El cumplimiento DIAN es lo más crítico y **no puede improvisarse**: se necesita validar con un PTA antes de facturar electrónicamente en producción.
- Errores en cálculos de impuestos o nómina generan pérdida de confianza rápido — cualquier cambio en `contabilidad/services.py` o el futuro módulo de nómina debe probarse con casos reales antes de desplegar.
- La adopción depende de que el onboarding sea simple — mantener el registro de empresa en un solo paso (ya implementado) como principio de diseño para todo lo nuevo.
