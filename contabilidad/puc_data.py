"""Catalogo de referencia del Plan Unico de Cuentas para comerciantes (PUC),
Decreto 2650 de 1993 (Colombia), a nivel de Clase / Grupo / Cuenta (4 digitos).

Esto es solo un panel de AYUDA/consulta para el usuario -- no tiene relacion
con las cuentas realmente sembradas por `contabilidad.services.sembrar_plan_cuentas`
(esas son un subconjunto minimo de ~12 cuentas para el motor contable del MVP).//
Aqui se muestra el catalogo completo a nivel de cuenta (4 digitos), que es el
mismo nivel de detalle que usa el motor contable de la app (ninguna parte del
sistema opera a nivel de subcuenta de 6 digitos).

Fuente: texto oficial del Decreto 2650 de 1993 (Clase 1) y puc.com.co
(Clases 2-9), cotejados entre si. No incluye subcuentas de 6 digitos (serian
miles de filas) ni la clase 7 a nivel de cuenta (el sitio fuente solo publica
esa clase a nivel de grupo).

Naturaleza: por defecto sigue la clase (Activo/Gasto/Costo = Debito; Pasivo/
Patrimonio/Ingreso = Credito), salvo las cuentas "contrapartida" marcadas
explicitamente en NATURALEZA_EXCEPCIONES (ej. depreciacion acumulada,
provisiones, devoluciones en ventas/compras, perdida del ejercicio).
"""

NATURALEZA_POR_CLASE = {
    "1": "DEBITO",   # Activo
    "2": "CREDITO",  # Pasivo
    "3": "CREDITO",  # Patrimonio
    "4": "CREDITO",  # Ingresos
    "5": "DEBITO",   # Gastos
    "6": "DEBITO",   # Costos de ventas
    "7": "DEBITO",   # Costos de produccion o de operacion
    "8": "DEBITO",   # Cuentas de orden deudoras
    "9": "CREDITO",  # Cuentas de orden acreedoras
}

# Cuentas "contrapartida" cuya naturaleza real es la opuesta a la de su clase.
NATURALEZA_EXCEPCIONES = {
    "1299": "CREDITO", "1399": "CREDITO", "1499": "CREDITO",
    "1592": "CREDITO", "1596": "CREDITO", "1597": "CREDITO", "1598": "CREDITO",
    "1599": "CREDITO", "1698": "CREDITO", "1699": "CREDITO", "1899": "CREDITO",
    "4175": "DEBITO", "4275": "DEBITO",
    "6225": "CREDITO",
    "3610": "DEBITO", "3710": "DEBITO",
}

PUC_CATALOGO = {
    "1": {
        "nombre": "Activo",
        "grupos": {
            "11": {"nombre": "Disponible", "cuentas": {
                "1105": "Caja", "1110": "Bancos", "1115": "Remesas en tránsito",
                "1120": "Cuentas de ahorro", "1125": "Fondos",
            }},
            "12": {"nombre": "Inversiones", "cuentas": {
                "1205": "Acciones", "1210": "Cuotas o partes de interés social", "1215": "Bonos",
                "1220": "Cédulas", "1225": "Certificados", "1230": "Papeles comerciales",
                "1235": "Títulos", "1240": "Aceptaciones bancarias o financieras",
                "1245": "Derechos fiduciarios", "1250": "Derechos de recompra de inversiones negociadas (repos)",
                "1255": "Obligatorias", "1260": "Cuentas en participación",
                "1295": "Otras inversiones", "1299": "Provisiones",
            }},
            "13": {"nombre": "Deudores", "cuentas": {
                "1305": "Clientes", "1310": "Cuentas corrientes comerciales",
                "1315": "Cuentas por cobrar a casa matriz", "1320": "Cuentas por cobrar a vinculados económicos",
                "1323": "Cuentas por cobrar a directores", "1325": "Cuentas por cobrar a socios y accionistas",
                "1328": "Aportes por cobrar", "1330": "Anticipos y avances",
                "1332": "Cuentas de operación conjunta", "1335": "Depósitos",
                "1340": "Promesas de compra venta", "1345": "Ingresos por cobrar",
                "1350": "Retención sobre contratos", "1355": "Anticipo de impuestos y contribuciones o saldos a favor",
                "1360": "Reclamaciones", "1365": "Cuentas por cobrar a trabajadores",
                "1370": "Préstamos a particulares", "1380": "Deudores varios",
                "1385": "Derechos de recompra de cartera negociada", "1390": "Deudas de difícil cobro",
                "1399": "Provisiones",
            }},
            "14": {"nombre": "Inventarios", "cuentas": {
                "1405": "Materias primas", "1410": "Productos en proceso",
                "1415": "Obras de construcción en curso", "1417": "Obras de urbanismo",
                "1420": "Contratos en ejecución", "1425": "Cultivos en desarrollo",
                "1428": "Plantaciones agrícolas", "1430": "Productos terminados",
                "1435": "Mercancías no fabricadas por la empresa", "1440": "Bienes raíces para la venta",
                "1445": "Semovientes", "1450": "Terrenos",
                "1455": "Materiales, repuestos y accesorios", "1460": "Envases y empaques",
                "1465": "Inventarios en tránsito", "1499": "Provisiones",
            }},
            "15": {"nombre": "Propiedades, planta y equipo", "cuentas": {
                "1504": "Terrenos", "1506": "Materiales proyectos petroleros",
                "1508": "Construcciones en curso", "1512": "Maquinaria y equipos en montaje",
                "1516": "Construcciones y edificaciones", "1520": "Maquinaria y equipo",
                "1524": "Equipo de oficina", "1528": "Equipo de computación y comunicación",
                "1532": "Equipo médico-científico", "1536": "Equipo de hoteles y restaurantes",
                "1540": "Flota y equipo de transporte", "1544": "Flota y equipo fluvial y/o marítimo",
                "1548": "Flota y equipo aéreo", "1552": "Flota y equipo férreo",
                "1556": "Acueductos, plantas y redes", "1560": "Armamento de vigilancia",
                "1562": "Envases y empaques", "1564": "Plantaciones agrícolas y forestales",
                "1568": "Vías de comunicación", "1572": "Minas y canteras",
                "1576": "Pozos artesianos", "1580": "Yacimientos",
                "1584": "Semovientes", "1588": "Propiedades, planta y equipo en tránsito",
                "1592": "Depreciación acumulada", "1596": "Depreciación diferida",
                "1597": "Amortización acumulada", "1598": "Agotamiento acumulado",
                "1599": "Provisiones",
            }},
            "16": {"nombre": "Intangibles", "cuentas": {
                "1605": "Crédito mercantil", "1610": "Marcas", "1615": "Patentes",
                "1620": "Concesiones y franquicias", "1625": "Derechos", "1630": "Know how",
                "1635": "Licencias", "1698": "Depreciación y/o amortización acumulada",
                "1699": "Provisiones",
            }},
            "17": {"nombre": "Diferidos", "cuentas": {
                "1705": "Gastos pagados por anticipado", "1710": "Cargos diferidos",
                "1715": "Costos de exploración por amortizar", "1720": "Costos de explotación y desarrollo",
                "1730": "Cargos por corrección monetaria diferida", "1798": "Amortización acumulada",
            }},
            "18": {"nombre": "Otros activos", "cuentas": {
                "1805": "Bienes de arte y cultura", "1895": "Diversos", "1899": "Provisiones",
            }},
            "19": {"nombre": "Valorizaciones", "cuentas": {
                "1905": "De inversiones", "1910": "De propiedades, planta y equipo",
                "1995": "De otros activos",
            }},
        },
    },
    "2": {
        "nombre": "Pasivo",
        "grupos": {
            "21": {"nombre": "Obligaciones financieras", "cuentas": {
                "2105": "Bancos nacionales", "2110": "Bancos del exterior",
                "2115": "Corporaciones financieras", "2120": "Compañías de financiamiento comercial",
                "2125": "Corporaciones de ahorro y vivienda", "2130": "Entidades financieras del exterior",
                "2135": "Compromisos de recompra de inversiones negociadas",
                "2140": "Compromisos de recompra de cartera negociada",
                "2145": "Obligaciones gubernamentales", "2195": "Otras obligaciones",
            }},
            "22": {"nombre": "Proveedores", "cuentas": {
                "2205": "Nacionales", "2210": "Del exterior", "2215": "Cuentas corrientes comerciales",
                "2220": "Casa matriz", "2225": "Compañías vinculadas",
            }},
            "23": {"nombre": "Cuentas por pagar", "cuentas": {
                "2305": "Cuentas corrientes comerciales", "2310": "A casa matriz",
                "2315": "A compañías vinculadas", "2320": "A contratistas",
                "2330": "Órdenes de compra por utilizar", "2335": "Costos y gastos por pagar",
                "2340": "Instalamentos por pagar", "2345": "Acreedores oficiales",
                "2350": "Regalías por pagar", "2355": "Deudas con accionistas o socios",
                "2357": "Deudas con directores", "2360": "Dividendos o participaciones por pagar",
                "2365": "Retención en la fuente", "2367": "Impuesto a las ventas retenido",
                "2368": "Impuesto de industria y comercio retenido",
                "2370": "Retenciones y aportes de nómina", "2375": "Cuotas por devolver",
                "2380": "Acreedores varios",
            }},
            "24": {"nombre": "Impuestos, gravámenes y tasas", "cuentas": {
                "2404": "De renta y complementarios", "2408": "Impuesto sobre las ventas por pagar",
                "2412": "De industria y comercio", "2416": "A la propiedad raíz",
                "2420": "Derechos sobre instrumentos públicos", "2424": "De valorización",
                "2428": "De turismo", "2432": "Tasa por utilización de puertos",
                "2436": "De vehículos", "2440": "De espectáculos públicos",
                "2444": "De hidrocarburos y minas",
                "2448": "Regalías e impuestos a la pequeña y mediana minería",
                "2452": "A las exportaciones cafeteras", "2456": "A las importaciones",
                "2460": "Cuotas de fomento", "2464": "De licores, cervezas y cigarrillos",
                "2468": "Al sacrificio de ganado", "2472": "Al azar y juegos",
                "2476": "Gravámenes y regalías por utilización del suelo", "2495": "Otros",
            }},
            "25": {"nombre": "Obligaciones laborales", "cuentas": {
                "2505": "Salarios por pagar", "2510": "Cesantías consolidadas",
                "2515": "Intereses sobre cesantías", "2520": "Prima de servicios",
                "2525": "Vacaciones consolidadas", "2530": "Prestaciones extralegales",
                "2532": "Pensiones por pagar", "2535": "Cuotas partes pensiones de jubilación",
                "2540": "Indemnizaciones laborales",
            }},
            "26": {"nombre": "Pasivos estimados y provisiones", "cuentas": {
                "2605": "Para costos y gastos", "2610": "Para obligaciones laborales",
                "2615": "Para obligaciones fiscales", "2620": "Pensiones de jubilación",
                "2625": "Para obras de urbanismo", "2630": "Para mantenimiento y reparaciones",
                "2635": "Para contingencias", "2640": "Para obligaciones de garantías",
                "2695": "Provisiones diversas",
            }},
            "27": {"nombre": "Diferidos", "cuentas": {
                "2705": "Ingresos recibidos por anticipado", "2710": "Abonos diferidos",
                "2715": "Utilidad diferida en ventas a plazos",
                "2720": "Crédito por corrección monetaria diferida", "2725": "Impuestos diferidos",
            }},
            "28": {"nombre": "Otros pasivos", "cuentas": {
                "2805": "Anticipos y avances recibidos", "2810": "Depósitos recibidos",
                "2815": "Ingresos recibidos para terceros", "2820": "Cuentas de operación conjunta",
                "2825": "Retenciones a terceros sobre contratos", "2830": "Embargos judiciales",
                "2835": "Acreedores del sistema", "2840": "Cuentas en participación",
                "2895": "Diversos",
            }},
            "29": {"nombre": "Bonos y papeles comerciales", "cuentas": {
                "2905": "Bonos en circulación", "2910": "Bonos obligatoriamente convertibles en acciones",
                "2915": "Papeles comerciales", "2920": "Bonos pensionales", "2925": "Títulos pensionales",
            }},
        },
    },
    "3": {
        "nombre": "Patrimonio",
        "grupos": {
            "31": {"nombre": "Capital social", "cuentas": {
                "3105": "Capital suscrito y pagado", "3115": "Aportes sociales",
                "3120": "Capital asignado", "3125": "Inversión suplementaria al capital asignado",
                "3130": "Capital de personas naturales", "3135": "Aportes del Estado",
                "3140": "Fondo social",
            }},
            "32": {"nombre": "Superávit de capital", "cuentas": {
                "3205": "Prima en colocación de acciones, cuotas o partes de interés social",
                "3210": "Donaciones", "3215": "Crédito mercantil", "3220": "Know how",
                "3225": "Superávit método de participación",
            }},
            "33": {"nombre": "Reservas", "cuentas": {
                "3305": "Reservas obligatorias", "3310": "Reservas estatutarias",
                "3315": "Reservas ocasionales",
            }},
            "34": {"nombre": "Revalorización del patrimonio", "cuentas": {
                "3405": "Ajustes por inflación", "3410": "Saneamiento fiscal",
                "3415": "Ajustes por inflación Decreto 3019 de 1989",
            }},
            "35": {"nombre": "Dividendos o participaciones", "cuentas": {
                "3505": "Dividendos decretados en acciones",
                "3510": "Participaciones decretadas en cuotas o partes de interés social",
            }},
            "36": {"nombre": "Resultados del ejercicio", "cuentas": {
                "3605": "Utilidad del ejercicio", "3610": "Pérdida del ejercicio",
            }},
            "37": {"nombre": "Resultados de ejercicios anteriores", "cuentas": {
                "3705": "Utilidades acumuladas", "3710": "Pérdidas acumuladas",
            }},
            "38": {"nombre": "Superávit por valorizaciones", "cuentas": {
                "3805": "De inversiones", "3810": "De propiedades, planta y equipo",
                "3895": "De otros activos",
            }},
        },
    },
    "4": {
        "nombre": "Ingresos",
        "grupos": {
            "41": {"nombre": "Operacionales", "cuentas": {
                "4105": "Agricultura, ganadería, caza y silvicultura", "4110": "Pesca",
                "4115": "Explotación de minas y canteras", "4120": "Industrias manufactureras",
                "4125": "Suministro de electricidad, gas y agua", "4130": "Construcción",
                "4135": "Comercio al por mayor y al por menor", "4140": "Hoteles y restaurantes",
                "4145": "Transporte, almacenamiento y comunicaciones", "4150": "Actividad financiera",
                "4155": "Actividades inmobiliarias, empresariales y de alquiler", "4160": "Enseñanza",
                "4165": "Servicios sociales y de salud",
                "4170": "Otras actividades de servicios comunitarios, sociales y personales",
                "4175": "Devoluciones en ventas",
            }},
            "42": {"nombre": "No operacionales", "cuentas": {
                "4205": "Otras ventas", "4210": "Financieros", "4215": "Dividendos y participaciones",
                "4218": "Ingresos método de participación", "4220": "Arrendamientos",
                "4225": "Comisiones", "4230": "Honorarios", "4235": "Servicios",
                "4240": "Utilidad en venta de inversiones",
                "4245": "Utilidad en venta de propiedades, planta y equipo",
                "4248": "Utilidad en venta de otros bienes", "4250": "Recuperaciones",
                "4255": "Indemnizaciones", "4260": "Participaciones en concesiones",
                "4265": "Ingresos de ejercicios anteriores", "4275": "Devoluciones en otras ventas",
                "4295": "Diversos",
            }},
            "47": {"nombre": "Ajustes por inflación", "cuentas": {
                "4705": "Corrección monetaria",
            }},
        },
    },
    "5": {
        "nombre": "Gastos",
        "grupos": {
            "51": {"nombre": "Operacionales de administración", "cuentas": {
                "5105": "Gastos de personal", "5110": "Honorarios", "5115": "Impuestos",
                "5120": "Arrendamientos", "5125": "Contribuciones y afiliaciones", "5130": "Seguros",
                "5135": "Servicios", "5140": "Gastos legales", "5145": "Mantenimiento y reparaciones",
                "5150": "Adecuación e instalación", "5155": "Gastos de viaje",
                "5160": "Depreciaciones", "5165": "Amortizaciones", "5195": "Diversos",
                "5199": "Provisiones",
            }},
            "52": {"nombre": "Operacionales de ventas", "cuentas": {
                "5205": "Gastos de personal", "5210": "Honorarios", "5215": "Impuestos",
                "5220": "Arrendamientos", "5225": "Contribuciones y afiliaciones", "5230": "Seguros",
                "5235": "Servicios", "5240": "Gastos legales", "5245": "Mantenimiento y reparaciones",
                "5250": "Adecuación e instalación", "5255": "Gastos de viaje",
                "5260": "Depreciaciones", "5265": "Amortizaciones",
                "5270": "Financieros-reajuste del sistema", "5275": "Pérdidas método de participación",
                "5295": "Diversos", "5299": "Provisiones",
            }},
            "53": {"nombre": "No operacionales", "cuentas": {
                "5305": "Financieros", "5310": "Pérdida en venta y retiro de bienes",
                "5313": "Pérdidas método de participación", "5315": "Gastos extraordinarios",
                "5395": "Gastos diversos",
            }},
            "54": {"nombre": "Impuesto de renta y complementarios", "cuentas": {
                "5405": "Impuesto de renta y complementarios",
            }},
            "59": {"nombre": "Ganancias y pérdidas", "cuentas": {
                "5905": "Ganancias y pérdidas",
            }},
        },
    },
    "6": {
        "nombre": "Costos de ventas",
        "grupos": {
            "61": {"nombre": "Costo de ventas y de prestación de servicios", "cuentas": {
                "6105": "Agricultura, ganadería, caza y silvicultura", "6110": "Pesca",
                "6115": "Explotación de minas y canteras", "6120": "Industrias manufactureras",
                "6125": "Suministro de electricidad, gas y agua", "6130": "Construcción",
                "6135": "Comercio al por mayor y al por menor", "6140": "Hoteles y restaurantes",
                "6145": "Transporte, almacenamiento y comunicaciones", "6150": "Actividad financiera",
                "6155": "Actividades inmobiliarias, empresariales y de alquiler", "6160": "Enseñanza",
                "6165": "Servicios sociales y de salud",
                "6170": "Otras actividades de servicios comunitarios, sociales y personales",
            }},
            "62": {"nombre": "Compras", "cuentas": {
                "6205": "De mercancías", "6210": "De materias primas", "6215": "De materiales indirectos",
                "6220": "Compra de energía", "6225": "Devoluciones en compras",
            }},
        },
    },
    "7": {
        "nombre": "Costos de producción o de operación",
        "grupos": {
            "71": {"nombre": "Materia prima", "cuentas": {}},
            "72": {"nombre": "Mano de obra directa", "cuentas": {}},
            "73": {"nombre": "Costos indirectos", "cuentas": {}},
            "74": {"nombre": "Contratos de servicios", "cuentas": {}},
        },
    },
    "8": {
        "nombre": "Cuentas de orden deudoras",
        "grupos": {
            "81": {"nombre": "Derechos contingentes", "cuentas": {
                "8105": "Bienes y valores entregados en custodia",
                "8110": "Bienes y valores entregados en garantía",
                "8115": "Bienes y valores en poder de terceros", "8120": "Litigios y/o demandas",
                "8125": "Promesas de compraventa", "8195": "Diversas",
            }},
            "82": {"nombre": "Deudoras fiscales", "cuentas": {}},
            "83": {"nombre": "Deudoras de control", "cuentas": {
                "8305": "Bienes recibidos en arrendamiento financiero",
                "8310": "Títulos de inversión no colocados",
                "8315": "Propiedades, planta y equipo totalmente depreciados, agotados y/o amortizados",
                "8320": "Créditos a favor no utilizados", "8325": "Activos castigados",
                "8330": "Títulos de inversión amortizados",
                "8335": "Capitalización por revalorización de patrimonio",
                "8395": "Otras cuentas deudoras de control", "8399": "Ajustes por inflación activos",
            }},
            "84": {"nombre": "Derechos contingentes por contra (CR)", "cuentas": {}},
            "85": {"nombre": "Deudoras fiscales por contra (CR)", "cuentas": {}},
            "86": {"nombre": "Deudoras de control por contra (CR)", "cuentas": {}},
        },
    },
    "9": {
        "nombre": "Cuentas de orden acreedoras",
        "grupos": {
            "91": {"nombre": "Responsabilidades contingentes", "cuentas": {
                "9105": "Bienes y valores recibidos en custodia",
                "9110": "Bienes y valores recibidos en garantía",
                "9115": "Bienes y valores recibidos de terceros", "9120": "Litigios y/o demandas",
                "9125": "Promesas de compraventa", "9130": "Contratos de administración delegada",
                "9135": "Cuentas en participación", "9195": "Otras responsabilidades contingentes",
            }},
            "92": {"nombre": "Acreedoras fiscales", "cuentas": {}},
            "93": {"nombre": "Acreedoras de control", "cuentas": {
                "9305": "Contratos de arrendamiento financiero",
                "9395": "Otras cuentas de orden acreedoras de control",
                "9399": "Ajustes por inflación patrimonio",
            }},
            "94": {"nombre": "Responsabilidades contingentes por contra (DB)", "cuentas": {}},
            "95": {"nombre": "Acreedoras fiscales por contra (DB)", "cuentas": {}},
            "96": {"nombre": "Acreedoras de control por contra (DB)", "cuentas": {}},
        },
    },
}


def naturaleza_de(codigo):
    if codigo in NATURALEZA_EXCEPCIONES:
        return NATURALEZA_EXCEPCIONES[codigo]
    return NATURALEZA_POR_CLASE[codigo[0]]


def construir_catalogo_plano():
    """Aplana PUC_CATALOGO en una lista de filas: clase, grupo y cuenta."""
    filas = []
    for clase_cod, clase in PUC_CATALOGO.items():
        filas.append({
            "codigo": clase_cod, "nombre": clase["nombre"], "nivel": "clase",
            "clase": clase_cod, "clase_nombre": clase["nombre"],
            "grupo": "", "grupo_nombre": "",
            "naturaleza": NATURALEZA_POR_CLASE[clase_cod],
        })
        for grupo_cod, grupo in clase["grupos"].items():
            filas.append({
                "codigo": grupo_cod, "nombre": grupo["nombre"], "nivel": "grupo",
                "clase": clase_cod, "clase_nombre": clase["nombre"],
                "grupo": grupo_cod, "grupo_nombre": grupo["nombre"],
                "naturaleza": NATURALEZA_POR_CLASE[clase_cod],
            })
            for cuenta_cod, cuenta_nombre in grupo["cuentas"].items():
                filas.append({
                    "codigo": cuenta_cod, "nombre": cuenta_nombre, "nivel": "cuenta",
                    "clase": clase_cod, "clase_nombre": clase["nombre"],
                    "grupo": grupo_cod, "grupo_nombre": grupo["nombre"],
                    "naturaleza": naturaleza_de(cuenta_cod),
                })
    return filas


PUC_CATALOGO_PLANO = construir_catalogo_plano()
