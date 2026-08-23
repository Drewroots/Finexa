# Roadmap y avance — NovaERP

Última actualización: 2026-08-22.

## Resumen de avance por fase

| Fase | Alcance original | Estado | Detalle |
|---|---|---|---|
| 1. Fundamentos | Autenticación, multi-tenant, modelo de datos base | ✅ **Hecho** | Login, registro de empresa, roles (Dueño/Contador/Vendedor), aislamiento por tenant. |
| 2. Facturación + Contabilidad básica | MVP facturable con reportes contables mínimos | ✅ **Hecho** | Facturación con ítems, emisión con asiento automático de partida doble, libro diario, balance de comprobación. |
| 3. Inventario + POS | Módulo de ventas físicas integrado | 🚧 **Parcial** | Inventario multi-producto con descuento automático y alertas de stock mínimo. **Falta:** POS offline-first, multi-bodega, código de barras. |
| 4. Cuentas por cobrar/pagar + flujo de caja | Automatización de cobros y proyecciones | 🚧 **Parcial** | CxC con saldo por factura, registro de pagos, flujo de caja proyectado a 30/60/90 días en el panel. **Falta:** recordatorios automáticos por WhatsApp/email, conciliación bancaria, módulo de cuentas por pagar a proveedores. |
| 5. Nómina electrónica | Cumplimiento DIAN nómina | ⏳ **Pendiente** | No iniciado. |
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
2. **Notas crédito/débito** sobre facturas ya emitidas (HU-35).
3. **Reportes financieros formales** — estado de resultados y balance general con formato NIIF pyme, no solo el balance de comprobación crudo (HU-43).
4. **Integración DIAN real** vía un Proveedor Tecnológico Autorizado — es el riesgo más crítico señalado en el documento de planeación original y debe validarse externamente antes de cualquier lanzamiento comercial (HU-33).
5. **Nómina electrónica** (fase 5 completa).
6. **Asistente con LLM real** conectado a los mismos KPIs que ya calcula `dashboard.services.calcular_kpis`, reemplazando las reglas por un modelo de lenguaje con contexto del negocio (HU-63).
7. **POS offline-first** para ventas físicas (React Native + SQLite local, como en el plan original) — hoy la facturación asume conexión permanente.

## Riesgos vigentes (heredados del documento de planeación)

- El cumplimiento DIAN es lo más crítico y **no puede improvisarse**: se necesita validar con un PTA antes de facturar electrónicamente en producción.
- Errores en cálculos de impuestos o nómina generan pérdida de confianza rápido — cualquier cambio en `contabilidad/services.py` o el futuro módulo de nómina debe probarse con casos reales antes de desplegar.
- La adopción depende de que el onboarding sea simple — mantener el registro de empresa en un solo paso (ya implementado) como principio de diseño para todo lo nuevo.
