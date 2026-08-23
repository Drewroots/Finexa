# Historias de usuario — NovaERP

Formato: **Como** `<rol>`, **quiero** `<acción>`, **para** `<beneficio>`.
Estado: ✅ Hecho (implementado en este MVP) · 🚧 Parcial · ⏳ Pendiente (roadmap).

## Módulo: Cuentas y acceso (`core`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-01 | Como dueño de pyme, quiero registrar mi empresa y mi usuario en un solo paso, para empezar a usar el sistema sin depender de soporte. | Se crea `Empresa` + `Usuario` (rol Dueño) + plan de cuentas base en una sola transacción. | ✅ |
| HU-02 | Como usuario, quiero iniciar y cerrar sesión de forma segura, para proteger la información financiera de mi negocio. | Login/logout con `django.contrib.auth`, contraseñas hasheadas, sesión expira. | ✅ |
| HU-03 | Como dueño, quiero invitar a mi contador o vendedores con roles distintos, para repartir el trabajo sin dar acceso total. | Vista `/equipo/` solo visible para rol Dueño; nuevo usuario queda asociado a la misma empresa. | ✅ |
| HU-04 | Como usuario, quiero que mis datos estén aislados de los de otras empresas (multi-tenant), para que no haya fugas de información entre clientes de NovaERP. | Todo `queryset` de negocio se filtra por `request.empresa`; probado con `EmpresaQuerysetMixin`. | ✅ |
| HU-05 | Como dueño, quiero recuperar mi contraseña por correo, para no quedar bloqueado del sistema. | Flujo de "olvidé mi contraseña" con envío de correo. | ⏳ |
| HU-06 | Como administrador de NovaERP, quiero autenticación multifactor, para cumplir buenas prácticas de seguridad. | 2FA opcional por TOTP. | ⏳ |

## Módulo: Clientes y proveedores (`clientes`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-10 | Como vendedor, quiero registrar clientes con su documento y datos de contacto, para poder facturarles. | CRUD completo, documento único por empresa. | ✅ |
| HU-11 | Como contador, quiero marcar un tercero como proveedor, cliente o ambos, para reutilizar el mismo registro en compras y ventas. | Campo `tipo` con las tres opciones. | ✅ |
| HU-12 | Como vendedor, quiero buscar un cliente por nombre o documento, para no perder tiempo en facturación. | Buscador con filtro `icontains` en la lista. | ✅ |

## Módulo: Inventario (`productos`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-20 | Como dueño, quiero registrar productos y servicios con precio y costo, para venderlos desde facturación. | CRUD de `Producto`, distingue producto (con stock) de servicio. | ✅ |
| HU-21 | Como dueño, quiero que el stock se descuente automáticamente al emitir una factura, para no llevar el inventario a mano. | `emitir_factura` genera `MovimientoInventario` tipo SALIDA por cada ítem. | ✅ |
| HU-22 | Como dueño, quiero ver alertas cuando un producto llega a su stock mínimo, para reabastecer a tiempo. | Panel muestra lista de productos bajo stock mínimo; fila resaltada en el listado. | ✅ |
| HU-23 | Como dueño, quiero ver el historial de movimientos de inventario, para auditar entradas y salidas. | Vista `/productos/movimientos/`. | ✅ |
| HU-24 | Como dueño con varias bodegas, quiero controlar stock por bodega, para saber qué hay en cada sede. | Modelo `Bodega` y stock por bodega; hoy el stock es único por empresa. | ⏳ |
| HU-25 | Como cajero, quiero un punto de venta offline-first con lectura de código de barras, para vender aunque se caiga internet. | App POS con SQLite local y sincronización diferida. | ⏳ |

## Módulo: Facturación electrónica (`facturacion`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-30 | Como vendedor, quiero crear una factura con varios ítems y ver el total con IVA calculado, para cobrarle al cliente. | Formulario + formset de ítems, cálculo de subtotal/IVA/total. | ✅ |
| HU-31 | Como dueño, quiero que al emitir una factura se genere automáticamente el asiento contable, para no duplicar el trabajo de captura. | `emitir_factura` crea `Transaccion` balanceada (CxC vs. Ingresos + IVA). | ✅ |
| HU-32 | Como dueño, quiero registrar pagos parciales o totales de una factura, para llevar el control de cartera. | `registrar_pago` actualiza saldo y genera asiento de conciliación; factura pasa a Pagada al saldar. | ✅ |
| HU-33 | Como contribuyente, quiero que mis facturas tengan numeración autorizada y firma digital ante la DIAN, para que sean válidas fiscalmente. | Integración con un Proveedor Tecnológico Autorizado (PTA) DIAN, CUFE, XML UBL 2.1. | ⏳ |
| HU-34 | Como cliente, quiero recibir mi factura por correo o WhatsApp automáticamente, para no tener que pedirla. | Envío automático post-emisión vía email/WhatsApp Business API. | ⏳ |
| HU-35 | Como dueño, quiero emitir notas crédito/débito sobre una factura, para corregir errores o descuentos posteriores. | Modelo `NotaCreditoDebito` ligado a la factura origen y su propio asiento. | ⏳ |

## Módulo: Contabilidad (`contabilidad`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-40 | Como contador, quiero un plan de cuentas base al crear la empresa, para no configurar todo desde cero. | `sembrar_plan_cuentas` crea ~12 cuentas base NIIF pyme automáticamente. | ✅ |
| HU-41 | Como contador, quiero ver el libro diario con todos los asientos, para revisar la trazabilidad de cada movimiento. | Vista `/contabilidad/libro-diario/` con detalle de movimientos por transacción. | ✅ |
| HU-42 | Como contador, quiero un balance de comprobación con el saldo de cada cuenta, para preparar los estados financieros. | Vista `/contabilidad/balance/` con débitos, créditos y saldo por cuenta. | ✅ |
| HU-43 | Como contador, quiero generar el balance general y el estado de resultados formales, para presentarlos a la DIAN o a un banco. | Reportes agrupados por tipo de cuenta con formato NIIF pyme. | ⏳ |
| HU-44 | Como contador, quiero un checklist de cierre contable mensual, para no olvidar ningún paso. | Módulo de cierre asistido con tareas marcables. | ⏳ |
| HU-45 | Como contador, quiero conciliar mis movimientos bancarios contra el extracto, para detectar diferencias. | Integración Open Banking + conciliación semiautomática. | ⏳ |

## Módulo: Nómina electrónica

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-50 | Como dueño, quiero liquidar la nómina de mis empleados con seguridad social y prestaciones, para cumplir la ley laboral. | Módulo `nomina` con liquidación automática. | ⏳ |
| HU-51 | Como dueño, quiero generar el documento electrónico de nómina ante la DIAN, para cumplir la normativa. | Integración DIAN nómina electrónica. | ⏳ |

## Módulo: Panel de decisión y asistente (`dashboard`)

| # | Historia | Criterios de aceptación | Estado |
|---|---|---|---|
| HU-60 | Como dueño, quiero ver en un panel las ventas del mes, la cartera por cobrar y el IVA por pagar, para tomar decisiones rápido. | `dashboard/index.html` con tarjetas de KPIs calculados en tiempo real. | ✅ |
| HU-61 | Como dueño, quiero ver un flujo de caja proyectado a 30/60/90 días, para anticipar necesidades de efectivo. | Cálculo por vencimiento de facturas pendientes. | ✅ |
| HU-62 | Como dueño, quiero preguntar en lenguaje natural cosas como "¿cuánto debo en impuestos?", para no tener que ir a buscar el dato en los reportes. | Asistente basado en reglas sobre los KPIs reales (v0, sin LLM externo). | ✅ (v0) |
| HU-63 | Como dueño, quiero que el asistente entienda preguntas libres y complejas, no solo frases predefinidas, para resolver dudas contables/tributarias reales. | Integración con un modelo de lenguaje (LLM) + contexto del negocio. | ⏳ |
| HU-64 | Como dueño, quiero soporte por chat en vivo 24/7, para resolver problemas sin esperar días. | Widget de chat en vivo + escalamiento a humano. | ⏳ |
