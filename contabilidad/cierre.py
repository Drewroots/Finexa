from .models import TareaCierre

# Checklist base que se instancia (idempotente) para cada mes que el usuario consulte.
TAREAS_CIERRE_BASE = [
    "Verificar que todas las facturas del mes estén emitidas o anuladas (ninguna en borrador)",
    "Registrar los pagos recibidos y actualizar la cartera pendiente",
    "Cargar y conciliar el extracto bancario del mes",
    "Calcular y verificar el IVA por pagar del periodo",
    "Revisar facturas vencidas y gestionar su cobro",
    "Verificar que el balance de comprobación cuadre (débitos = créditos)",
    "Hacer una copia de seguridad de la base de datos",
]


def obtener_o_crear_checklist(empresa, anio, mes):
    """Devuelve las tareas de cierre del mes, creándolas (idempotente) si no existen."""
    tareas = []
    for orden, descripcion in enumerate(TAREAS_CIERRE_BASE, start=1):
        tarea, creada = TareaCierre.objects.get_or_create(
            empresa=empresa,
            anio=anio,
            mes=mes,
            descripcion=descripcion,
            defaults={"orden": orden},
        )
        if not creada and tarea.orden != orden:
            tarea.orden = orden
            tarea.save(update_fields=["orden"])
        tareas.append(tarea)
    return sorted(tareas, key=lambda t: t.orden)
