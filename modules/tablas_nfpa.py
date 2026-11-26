
# ElectraSafety Consultores
# Referencia: NFPA 70E, edición 2027
# Datos de la traducción suministrada para el proyecto.

TABLA_CA = {
    "Tablero de distribución hasta 240 V": [
        (1, 240, 25, 0.03, 455, 1, 0.485)
    ],
    "Tablero de distribución de más de 240 V hasta 600 V": [
        (241, 600, 25, 0.03, 455, 2, 0.9)
    ],
    "Centro de control de motores MCC clase 600 V": [
        (1, 600, 65, 0.03, 455, 2, 1.5),
        (1, 600, 42, 0.33, 455, 4, 4.3)
    ],
    "Equipo de maniobra o cuadro de distribución clase 600 V": [
        (1, 600, 35, 0.5, 455, 4, 6)
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
    ]
}

# Tensión máxima, límite móvil,
# límite fijo y límite restringido.
# Distancias expresadas en metros.

CHOQUE_CA = [
    (49, None, None, None),
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
    (49, None, None, None),
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

GUANTES = [
    ("00", 500, 750),
    ("0", 1000, 1500),
    ("1", 7500, 11250),
    ("2", 17000, 25500),
    ("3", 26500, 39750),
    ("4", 36000, 54000)
]

PROTECCION_ARCO = {
    1: 4,
    2: 8,
    3: 25,
    4: 40
}


def calcular_arco(
    sistema, equipo, voltaje,
    corriente, tiempo, distancia
):

    if min(voltaje, corriente, tiempo, distancia) <= 0:
        return {
            "aplicable": False,
            "motivo": "Los parámetros deben ser positivos."
        }

    if sistema == "CA":

        filas = TABLA_CA.get(equipo, [])
        resultados = []

        for fila in filas:

            vmin, vmax, imax, tmax, dmin, cat, frontera = fila

            if (
                vmin <= voltaje <= vmax
                and corriente <= imax
                and tiempo <= tmax
                and distancia >= dmin
            ):

                resultados.append({
                    "aplicable": True,
                    "categoria": cat,
                    "frontera": frontera,
                    "corriente_maxima": imax,
                    "tiempo_maximo": tmax,
                    "distancia_minima": dmin,
                    "referencia": "130.7(C)(15)(a)"
                })

        if resultados:

            # Si coinciden varias filas, se conserva
            # la alternativa más conservadora.
            return max(
                resultados,
                key=lambda x: (
                    x["categoria"],
                    x["frontera"]
                )
            )

    elif sistema == "CC":

        if (
            equipo == "Baterías y equipos de CC"
            and 150 < voltaje <= 600
            and tiempo <= 2
            and distancia >= 455
            and corriente < 10
        ):

            if corriente < 1.5:
                cat, frontera = 2, 0.9

            elif corriente < 3:
                cat, frontera = 2, 1.2

            elif corriente < 7:
                cat, frontera = 3, 1.8

            else:
                cat, frontera = 4, 2.5

            return {
                "aplicable": True,
                "categoria": cat,
                "frontera": frontera,
                "tiempo_maximo": 2,
                "distancia_minima": 455,
                "referencia": "130.7(C)(15)(b)"
            }

    return {
        "aplicable": False,
        "motivo": (
            "No se cumplen las condiciones de las "
            "filas implementadas. No asignar una "
            "categoría de EPP mediante esta herramienta. "
            "Se requiere revisión técnica y, cuando "
            "corresponda, análisis de energía incidente."
        )
    }


def limites_choque(sistema, voltaje, movil=False):

    if sistema not in ("CA", "CC") or voltaje <= 0:
        return None

    tabla = CHOQUE_CA if sistema == "CA" else CHOQUE_CC

    for maximo, limite_movil, fijo, restringido in tabla:

        if voltaje <= maximo:

            return {
                "limitada": limite_movil if movil else fijo,
                "restringida": restringido,
                "referencia": (
                    "130.4(E)(a)" if sistema == "CA"
                    else "130.4(E)(b)"
                )
            }

    return None


def clase_guante(sistema, voltaje):

    if sistema not in ("CA", "CC") or voltaje <= 0:
        return None

    for clase, ca, cc in GUANTES:

        maximo = ca if sistema == "CA" else cc

        if voltaje <= maximo:
            return clase

    return None
