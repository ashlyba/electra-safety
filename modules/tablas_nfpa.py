import math


# ElectraSafety Consultores
# Electra Safe 360
# Referencia académica: NFPA 70E 2027.
# Método de categorías de EPP.


TABLA_CA = {
    "Tablero de distribución hasta 240 V": [
        (0, 240, 25, 0.03, 455, 1, 0.485)
    ],

    "Tablero de distribución de más de 240 V hasta 600 V": [
        (240, 600, 25, 0.03, 455, 2, 0.9)
    ],

    "Centro de control de motores MCC clase 600 V": [
        (0, 600, 65, 0.03, 455, 2, 1.5),
        (0, 600, 42, 0.33, 455, 4, 4.3)
    ],

    "Equipo de maniobra o cuadro de distribución clase 600 V": [
        (0, 600, 35, 0.5, 455, 4, 6)
    ],

    "Otros equipos clase 600 V": [
        (277, 600, 65, 0.03, 455, 2, 1.5)
    ],

    "Arrancador de motores NEMA E2": [
        (2300, 7200, 35, 0.24, 910, 4, 12)
    ],

    "Equipo de maniobra metal-clad": [
        (1000, 15000, 35, 0.24, 910, 4, 12)
    ],

    "Interruptores en envolvente metálica": [
        (1000, 15000, 35, 0.24, 910, 4, 12)
    ],

    "Otros equipos de 1 kV a 15 kV": [
        (1000, 15000, 35, 0.24, 910, 4, 12)
    ],

    "Equipo resistente al arco hasta clase 600 V": [],

    "Equipo resistente al arco de 1 kV a 15 kV": []
}


# Límites de aproximación por choque eléctrico.
# Voltaje máximo, conductor móvil, parte fija,
# límite de aproximación restringida.
# Distancias expresadas en metros.

CHOQUE_CA = [
    (150, 3.1, 1.0, "Evitar contacto"),
    (750, 3.1, 1.0, 0.31),
    (5000, 3.1, 1.0, 0.63),
    (15000, 3.1, 1.5, 0.65),
    (36000, 3.1, 1.8, 0.77),
    (46000, 3.1, 2.5, 0.84),
    (72500, 3.1, 2.5, 1.0),
    (121000, 3.3, 2.5, 1.2),
    (145000, 3.4, 3.1, 1.3),
    (169000, 3.6, 3.6, 1.5),
    (242000, 4.0, 4.0, 2.1),
    (362000, 4.7, 4.7, 3.5),
    (420000, 5.8, 5.8, 4.3),
    (550000, 5.8, 5.8, 5.1),
    (800000, 7.2, 7.2, 6.9)
]


CHOQUE_CC = [
    (300, 3.1, 1.0, "Evitar contacto"),
    (1000, 3.1, 1.0, 0.3),
    (5000, 3.1, 1.5, 0.5),
    (15000, 3.1, 1.5, 0.7),
    (45000, 3.1, 2.5, 0.8),
    (75000, 3.1, 2.5, 1.0),
    (150000, 3.3, 3.1, 1.2),
    (250000, 3.6, 3.6, 1.6),
    (500000, 6.0, 6.0, 3.5),
    (800000, 8.0, 8.0, 5.0)
]


# Clase de guante y tensión máxima de utilización.
# Clase, voltaje CA, voltaje CC.

GUANTES = [
    ("00", 500, 750),
    ("0", 1000, 1500),
    ("1", 7500, 11250),
    ("2", 17000, 25500),
    ("3", 26500, 39750),
    ("4", 36000, 54000)
]


# Clasificación mínima de protección contra arco.
# Valores expresados en cal/cm2.

PROTECCION_ARCO = {
    1: 4,
    2: 8,
    3: 25,
    4: 40
}


def no_aplicable(motivo):
    return {
        "aplicable": False,
        "motivo": motivo,
        "categoria": None,
        "frontera": None
    }


def numero_positivo(valor):
    if isinstance(valor, bool) or type(valor).__name__ == "bool_":
        return None

    try:
        numero = float(valor)

        if not math.isfinite(numero):
            return None

        if numero <= 0:
            return None

        return numero

    except (ValueError, TypeError, OverflowError):
        return None


def calcular_arco(
    sistema,
    equipo,
    voltaje,
    corriente,
    tiempo,
    distancia,
    fila_mcc=None
):
    if sistema not in ("CA", "CC"):
        return no_aplicable(
            "Sistema eléctrico no reconocido."
        )

    parametros = [
        numero_positivo(voltaje),
        numero_positivo(corriente),
        numero_positivo(tiempo),
        numero_positivo(distancia)
    ]

    if any(valor is None for valor in parametros):
        return no_aplicable(
            "Los parámetros deben ser numéricos, "
            "finitos y mayores que cero."
        )

    voltaje, corriente, tiempo, distancia = parametros

    if sistema == "CA":
        if equipo not in TABLA_CA:
            return no_aplicable(
                "Equipo no incluido en las tablas."
            )

        if equipo.startswith("Equipo resistente al arco"):
            return no_aplicable(
                "Se requiere comprobar la clasificación "
                "del fabricante y las condiciones "
                "especiales de la tabla. "
                "No se asigna categoría automáticamente."
            )

        resultados = []

        for fila in TABLA_CA[equipo]:
            (
                vmin,
                vmax,
                imax,
                tmax,
                dmin,
                categoria,
                frontera
            ) = fila

            tension_valida = vmin <= voltaje <= vmax

            if equipo == (
                "Tablero de distribución de más "
                "de 240 V hasta 600 V"
            ):
                tension_valida = 240 < voltaje <= 600

            if (
                tension_valida
                and corriente <= imax
                and tiempo <= tmax
                and distancia >= dmin
            ):
                resultados.append({
                    "aplicable": True,
                    "categoria": categoria,
                    "frontera": frontera,
                    "corriente_maxima": imax,
                    "tiempo_maximo": tmax,
                    "distancia_minima": dmin,
                    "referencia": "130.7(C)(15)(a)",
                    "metodo": "Método de tablas",
                    "proteccion_minima":
                        PROTECCION_ARCO[categoria]
                })

        if resultados:
            if equipo.startswith("Centro de control de motores") and fila_mcc is not None:
                resultados = [fila for fila in resultados if fila["categoria"] == fila_mcc]
                if not resultados:
                    return no_aplicable("La fila MCC documentada no cumple los límites ingresados.")
            if len(resultados) > 1:
                return no_aplicable("Coinciden dos filas MCC. Identifique y documente la fila aplicable.")
            resultado = resultados[0]
            resultado["filas_coincidentes"] = 1
            return resultado

    elif sistema == "CC":
        if equipo != "Baterías y equipos de CC":
            return no_aplicable(
                "Equipo de corriente continua "
                "fuera del alcance implementado."
            )

        if not (
            150 < voltaje <= 600
            and tiempo <= 2
            and distancia >= 455
            and corriente < 10
        ):
            return no_aplicable(
                "Los parámetros no coinciden "
                "con el alcance de corriente continua."
            )

        if corriente < 1.5:
            categoria = 2
            frontera = 0.9

        elif corriente < 3:
            categoria = 2
            frontera = 1.2

        elif corriente < 7:
            categoria = 3
            frontera = 1.8

        else:
            categoria = 4
            frontera = 2.5

        return {
            "aplicable": True,
            "categoria": categoria,
            "frontera": frontera,
            "tiempo_maximo": 2,
            "distancia_minima": 455,
            "referencia": "130.7(C)(15)(b)",
            "metodo": "Método de tablas",
            "proteccion_minima":
                PROTECCION_ARCO[categoria],
            "observacion": (
                "Resultado preliminar. Verificar "
                "las condiciones y notas de la tabla."
            )
        }

    return no_aplicable(
        "No se cumplen las condiciones de las "
        "filas implementadas. No asignar categoría "
        "mediante esta herramienta. Se requiere "
        "revisión técnica especializada."
    )


def limites_choque(
    sistema,
    voltaje,
    movil=False,
    *,
    base_ca=None,
    fase_tierra=None,
    altitud=0
):
    voltaje = numero_positivo(voltaje)

    if (
        sistema not in ("CA", "CC")
        or voltaje is None
        or isinstance(altitud, bool)
        or not isinstance(altitud, (int, float))
        or not math.isfinite(altitud)
    ):
        return None

    referencia = (
        "130.4(E)(a)"
        if sistema == "CA"
        else "130.4(E)(b)"
    )

    if sistema == "CA" and base_ca == "monofasico":
        fase_tierra = numero_positivo(fase_tierra)
        if fase_tierra is None:
            return None
        if voltaje > 250:
            voltaje = fase_tierra * 1.732

    if voltaje < 50:
        return {
            "limitada": None,
            "restringida": None,
            "referencia": referencia,
            "observacion": (
                "Sin distancia tabulada para este "
                "intervalo de tensión. Esto no implica "
                "ausencia de peligros eléctricos."
            )
        }

    tabla = (
        CHOQUE_CA
        if sistema == "CA"
        else CHOQUE_CC
    )

    minimos = (
        (50, 151, 751, 5100, 15100, 36100, 46100, 72600, 121100, 145100,
         169100, 242100, 362100, 420100, 550100)
        if sistema == "CA" else (50, 301, 1100, 5100, 15100, 45100, 75100, 150100, 250100, 500100)
    )
    if sistema == "CA" and base_ca == "nota_e":
        a_tierra = numero_positivo(fase_tierra)
        if a_tierra is None or a_tierra > 240:
            return None
        voltaje = 150

    if base_ca == "monofasico" and sistema == "CA":
        # Selección conservadora al redondear al siguiente umbral publicado.
        if not any(lo <= voltaje <= row[0] for lo, row in zip(minimos, tabla)):
            voltaje = next((lo for lo in minimos if lo >= voltaje), voltaje)

    for minimo, (maximo, limite_movil, fijo, restringido) in zip(minimos, tabla):
        if minimo <= voltaje <= maximo:
            return {
                "limitada":
                    limite_movil if movil else fijo,
                "restringida": (
                    "Requiere revisión por altitud"
                    if altitud > 900 and isinstance(restringido, (int, float))
                    else restringido
                ),
                "referencia": referencia,
                "observacion": (
                    "Verificar notas, altitud y "
                    "condiciones de exposición."
                )
            }

    return None


def clase_guante(sistema, voltaje):
    voltaje = numero_positivo(voltaje)

    if (
        sistema not in ("CA", "CC")
        or voltaje is None
    ):
        return None

    for clase, ca, cc in GUANTES:
        maximo = ca if sistema == "CA" else cc

        if voltaje <= maximo:
            return clase

    return None


# Evaluación de la probabilidad de ocurrencia
# de un incidente de arco eléctrico.
# Tarea, condición del equipo, probabilidad.


TAREAS_ARCO = [
    (
        "Lectura de un medidor de panel mientras "
        "se opera un interruptor del medidor.",
        "Cualquiera",
        "No"
    ),
    (
        "Termografía infrarroja y otras inspecciones "
        "sin contacto fuera del límite restringido, "
        "sin apertura de puertas o cubiertas.",
        "Cualquiera",
        "No"
    ),
    (
        "Trabajo en circuitos de control de hasta "
        "125 V CA o CC, sin otros equipos energizados "
        "expuestos de tensión superior.",
        "Cualquiera",
        "No"
    ),
    (
        "Examen de cables aislados sin manipulación.",
        "Cualquiera",
        "No"
    ),
    (
        "Mantenimiento de una sola celda de baterías "
        "o unidades multicelda en bastidor abierto.",
        "Cualquiera",
        "No"
    ),
    (
        "Trabajo en equipos de baterías de menos "
        "de 600 V con separación entre conductores "
        "expuestos superior a 1 mm por voltio.",
        "Cualquiera",
        "No"
    ),
    (
        "Trabajo en conductores energizados de CA "
        "y partes de circuitos, incluidas pruebas.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Primera operación de un interruptor "
        "después de su instalación o mantenimiento.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Trabajo en conductores energizados de CC "
        "de celdas de baterías conectadas en serie, "
        "incluidas pruebas eléctricas.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Retirada o instalación de interruptores "
        "automáticos o interruptores.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Apertura o retirada de puertas y cubiertas "
        "que expongan conductores energizados desnudos "
        "o partes de circuitos.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Aplicación de puesta a tierra temporal "
        "de protección después de la prueba de tensión.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Trabajo en circuitos de control con "
        "conductores energizados expuestos "
        "de más de 120 V.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Inserción o extracción de unidades "
        "arrancadoras de un MCC.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Inserción o extracción de interruptores "
        "o arrancadores de sus compartimentos.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Inserción o extracción de dispositivos "
        "enchufables en canalizaciones de barras.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Examen de cables aislados con manipulación.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Trabajo en conductores energizados expuestos "
        "de equipos alimentados directamente por "
        "tableros de distribución o MCC.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Inserción o extracción de medidores "
        "de facturación kWh a tensión y corriente primarias.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Inserción o extracción de cubiertas "
        "de conectores entre celdas de baterías.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Trabajo en conductores energizados expuestos "
        "de equipos alimentados directamente "
        "por una fuente de CC.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Apertura de compartimentos de transformadores "
        "de tensión o alimentación de control.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Operación de desconexión exterior mediante "
        "pértiga de 1 kV a 15 kV.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Operación de desconexión exterior de "
        "accionamiento conjunto desde el suelo, "
        "de 1 kV a 15 kV.",
        "Cualquiera",
        "Sí"
    ),
    (
        "Operación de interruptor automático, "
        "interruptor, contactor o arrancador.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Pruebas de tensión en celdas individuales "
        "o unidades multicelda individuales.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Retirada o instalación de cubiertas "
        "sin exposición de conductores energizados "
        "desnudos ni partes de circuitos.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Apertura de puertas de tableros para acceder "
        "a dispositivos de sobrecorriente de frente muerto.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Retirada de cubiertas no conductoras "
        "de conectores entre celdas de baterías.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Mantenimiento y pruebas de celdas individuales "
        "o unidades multicelda en bastidor abierto.",
        "Normal / Anormal",
        "No / Sí"
    ),
    (
        "Inserción o extracción de celdas individuales "
        "o unidades multicelda en bastidor abierto.",
        "Normal / Anormal",
        "No / Sí"
    )
]


def probabilidad_arco(indice, estado, sistema=None, tension_tarea=None, separacion_mm=None):
    if type(indice) is not int:
        return None

    if not 0 <= indice < len(TAREAS_ARCO):
        return None

    if sistema == "CA" and indice in {4, 5, 8, 19, 20, 25, 28, 29, 30}:
        return None
    if sistema == "CC" and indice == 6:
        return None
    if tension_tarea is not None and indice in {2, 5, 12, 22, 23}:
        tension = numero_positivo(tension_tarea)
        separacion = numero_positivo(separacion_mm)
        if tension is None:
            return None
        if indice == 2 and tension > 125:
            return None
        if indice == 5 and not (tension < 600 and separacion is not None and separacion > tension):
            return None
        if indice == 12 and tension <= 120:
            return None
        if indice in {22, 23} and not 1000 <= tension <= 15000:
            return None
    valor = TAREAS_ARCO[indice][2]

    if valor == "No / Sí":
        return {
            "Normal": False,
            "Anormal": True
        }.get(estado)

    return valor == "Sí"


REVISION_CRITERIOS = 2


def resultado_arco_vigente(detalle):
    """Comprueba que el punto puede reutilizarse con los criterios actuales."""
    if detalle.get("Versión de criterios de arco") != REVISION_CRITERIOS:
        return False
    if detalle.get("Método aplicable") != "Sí" or detalle.get("Probabilidad de arco") != "Sí":
        return False
    if not all(detalle.get(campo) is True for campo in (
        "Requiere EPP contra arco", "Clasificación verificada", "Mantenimiento verificado",
        "Notas verificadas", "Método exclusivo de tablas"
    )):
        return False
    if not all(str(detalle.get(campo) or "").strip() for campo in (
        "Justificación de tarea", "Evidencia normativa", "Fuente de datos", "Responsable"
    )):
        return False
    if detalle.get("Sistema") == "CC" and detalle.get("Condición de CC") != "Al aire libre, sin exposición a electrolito":
        return False
    if detalle.get("Condición del equipo") == "Normal" and detalle.get("Condición normal verificada") is not True:
        return False
    if probabilidad_arco(
        detalle.get("Índice de fila de tarea"), detalle.get("Condición del equipo"), detalle.get("Sistema"),
        detalle.get("Tensión de la tarea (V)", 0), detalle.get("Separación entre conductores (mm)")
    ) is not True or detalle.get("Condición del equipo") not in {"Normal", "Anormal"}:
        return False
    calculo = calcular_arco(
        detalle.get("Sistema"), detalle.get("Tipo de equipo"), detalle.get("Tensión (V)"),
        detalle.get("Corriente de falla (kA)"), detalle.get("Tiempo (s)"),
        detalle.get("Distancia de trabajo (mm)"), detalle.get("Fila MCC")
    )
    return (
        calculo["aplicable"]
        and str(calculo["categoria"]) == str(detalle.get("Categoría"))
        and calculo["frontera"] == numero_positivo(detalle.get("Frontera de arco"))
        and calculo["proteccion_minima"] == numero_positivo(detalle.get("Protección mínima"))
        and calculo["referencia"] == detalle.get("Referencia arco")
    )
