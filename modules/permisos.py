import streamlit as st

from database import consultar

from modules.comunes import (
    seleccionar_proyecto,
    advertencia_tecnica
)

from modules.documentos import administrar_documentos, estado_documental
from modules.tablas_nfpa import resultado_arco_vigente


ENERGIZADO = {
    "1. Identificación del trabajo": [
        "Identificación",
        "Equipo",
        "Ubicación",
        "Fecha y horario",
        "Descripción y alcance de la tarea",
        "Circuito y fuentes de energía",
        "Tareas individuales y peligros eléctricos"
    ],
    "2. Justificación y necesidad del permiso": [
        "Justificación del trabajo energizado",
        "Evaluación de necesidad del permiso",
        "Trabajo dentro del límite restringido",
        "Interacción con partes no expuestas y mayor probabilidad de lesión por arco",
        "Excepción aplicable y fundamento"
    ],
    "3. Evaluaciones técnicas": [
        "Referencia de evaluación de riesgos",
        "Referencia de evaluación de arco",
        "Tensión nominal",
        "Tensión de exposición al choque",
        "Resultado de evaluación de choque",
        "Resultado de evaluación de arco",
        "Referencia y revisión del análisis técnico",
        "Frontera de arco eléctrico",
        "Límite de aproximación limitada",
        "Límite de aproximación restringida",
        "EPP requerido",
        "EPP y protección contra choque",
        "EPP y protección contra arco"
    ],
    "4. Medidas de protección": [
        "Prácticas de trabajo",
        "Precauciones y controles de las fuentes de energía",
        "Herramientas y equipos",
        "Delimitación del área",
        "Control de acceso",
        "Condiciones de suspensión"
    ],
    "5. Personal y planificación": [
        "Personal calificado",
        "Persona calificada que preparó el plan",
        "Persona adicional y posición de seguridad",
        "Competencias y funciones",
        "Reunión informativa previa",
        "Evidencia de reunión, asistentes y peligros discutidos",
        "Previsiones de emergencia",
        "Medios de comunicación y rescate"
    ],
    "6. Responsabilidades": [
        "Responsable de ejecución",
        "Responsable de seguridad",
        "Responsable de revisión",
        "Responsable de aprobación",
        "Observaciones"
    ]
}


DESENERGIZADO = {
    "1. Información general": [
        "Identificación",
        "Equipo",
        "Ubicación",
        "Fecha y horario",
        "Descripción y alcance de la tarea",
        "Circuito y fuentes de energía",
        "Tareas individuales y peligros eléctricos"
    ],
    "2. Identificación y aislamiento": [
        "Fuentes de energía",
        "Puntos de aislamiento",
        "Parada, apertura y comprobación de desconexiones",
        "Dispositivos de aislamiento",
        "Referencia del procedimiento LOTO",
        "Participantes",
        "Candados y etiquetas"
    ],
    "3. Condición eléctricamente segura": [
        "Tratamiento de energía almacenada",
        "Instrumento de verificación",
        "Comprobación del instrumento",
        "Puesta a tierra temporal y pruebas adicionales",
        "Verificación de ausencia de tensión",
        "Resultados de la verificación",
        "Responsable de verificación",
        "Liberación documentada para trabajar"
    ],
    "4. Ejecución del trabajo": [
        "Medidas de protección",
        "Persona calificada que preparó el plan",
        "Reunión informativa previa",
        "Condiciones de suspensión",
        "Previsiones de emergencia",
        "Responsable de ejecución"
    ],
    "5. Cierre y restitución": [
        "Inspección final",
        "Retiro de herramientas",
        "Retiro de bloqueos y etiquetas",
        "Notificación al personal",
        "Restitución del servicio",
        "Responsable de revisión",
        "Responsable de aprobación",
        "Observaciones"
    ]
}


DECISION = "Evaluación de necesidad del permiso"
LIMITE = "Trabajo dentro del límite restringido"
INTERACCION = "Interacción con partes no expuestas y mayor probabilidad de lesión por arco"
EXCEPCION = "Excepción aplicable y fundamento"
PERSONA_ADICIONAL = "Persona adicional y posición de seguridad"
RESULTADO_ARCO = "Resultado de evaluación de arco"
FRONTERA = "Frontera de arco eléctrico"
EPP_CHOQUE = "EPP y protección contra choque"
EPP_ARCO = "EPP y protección contra arco"
DECISIONES = ("Requerido", "Exención documentada", "Fuera de los supuestos de 130.3(A)")
OPCIONES_ENERGIZADO = {
    DECISION: DECISIONES, LIMITE: ("Sí", "No"), INTERACCION: ("Sí", "No")
}
OPCION_EXENCION = "Supuesto de exención 130.3(C)"
EXENCIONES = (
    "Pruebas, localización de fallas o mediciones de tensión",
    "Termografía, ultrasonido o inspección visual sin cruzar el límite restringido",
    "Ingreso o salida sin trabajo eléctrico ni cruce del límite restringido",
    "Limpieza general u otra tarea no eléctrica sin cruzar el límite restringido"
)
ENERGIZADO["2. Justificación y necesidad del permiso"].append(OPCION_EXENCION)
OPCIONES_ENERGIZADO[OPCION_EXENCION] = EXENCIONES

AYUDAS = {
    "Justificación del trabajo energizado": "Describe el fundamento y la evidencia según 110.2(B).",
    EXCEPCION: "Si seleccionaste una exención, documenta su alcance, persona calificada, prácticas seguras y EPP según 130.3(C).",
    "Referencia y revisión del análisis técnico": "Indica fuente, fila y revisión. Usa resultados documentados del método de tablas.",
    "EPP requerido": "Resume el conjunto seleccionado y registra cada protección en los campos de choque y arco.",
    PERSONA_ADICIONAL: "Si 130.2(A)(2) aplica, registra nombre, formación en emergencias y posición fuera del límite o frontera mayor.",
    "Reunión informativa previa": "Registra quién dirige la reunión y los temas del plan y permiso. Actualiza la planificación al cambiar el alcance.",
    "Liberación documentada para trabajar": "Registra el responsable, criterio, fecha y evidencia de liberación en el escenario académico.",
    "Verificación de ausencia de tensión": "Identifica puntos y pares de medición o fundamenta la excepción aplicable de 120.6(7).",
    "Comprobación del instrumento": "Describe las comprobaciones en una fuente conocida antes y después de la prueba, según corresponda.",
    "Puesta a tierra temporal y pruebas adicionales": "Documenta cuándo procede según 120.6(7)–(9), o justifica su inaplicabilidad.",
    "Condiciones de suspensión": "Incluye cambios de alcance o condiciones, y cómo se replanifica y comunica el cambio."
}
NO_APLICA = {"n/a", "na", "no", "ninguno", "no aplica", "no aplicable"}
PENDIENTES = {"", "-", "—", "pendiente", "por definir", "sin datos", "no determinado", "no determinada"}


def texto(detalle, campo):
    return str(detalle.get(campo) or "").strip()


def validar_permiso(detalle, energizado, puntos=None, procedimientos=None, riesgos=None):
    secciones = ENERGIZADO if energizado else DESENERGIZADO
    opcionales = {"Observaciones", OPCION_EXENCION, EXCEPCION}
    faltantes = []
    for campos in secciones.values():
        for campo in campos:
            if campo in opcionales or campo in OPCIONES_ENERGIZADO:
                continue
            valor = texto(detalle, campo).casefold()
            if (valor.rstrip(" .:") in PENDIENTES | NO_APLICA
                    or valor.startswith(("requiere revisión", "pendiente de reevaluación"))):
                faltantes.append(campo)

    if energizado:
        decision = texto(detalle, DECISION)
        cruce = texto(detalle, LIMITE)
        interaccion = texto(detalle, INTERACCION)
        if decision not in DECISIONES or cruce not in ("Sí", "No") or interaccion not in ("Sí", "No"):
            faltantes.append("Selecciona la decisión y responde ambas condiciones de 130.3(A).")
        if decision == DECISIONES[0] and cruce != "Sí" and interaccion != "Sí":
            faltantes.append("Identifica al menos una condición que exige permiso según 130.3(A).")
        if decision == DECISIONES[2] and (cruce == "Sí" or interaccion == "Sí"):
            faltantes.append("La decisión sobre el permiso contradice las condiciones registradas.")
        if decision == DECISIONES[1]:
            exencion = texto(detalle, OPCION_EXENCION)
            fundamento = texto(detalle, EXCEPCION).casefold()
            if exencion not in EXENCIONES or fundamento in PENDIENTES | NO_APLICA:
                faltantes.append("Selecciona y fundamenta la exención de 130.3(C).")
            if cruce == "Sí" and exencion in EXENCIONES[1:]:
                faltantes.append("La exención seleccionada no admite cruzar el límite restringido.")
        if decision == DECISIONES[0]:
            epp = [texto(detalle, campo).casefold() for campo in (EPP_CHOQUE, EPP_ARCO)]
            if any(not v.startswith(("no aplica.", "no aplica:", "sin epp.", "sin epp:")) for v in epp):
                if texto(detalle, PERSONA_ADICIONAL).casefold().startswith(("no aplica", "sin persona")):
                    faltantes.append("Documenta la persona adicional requerida por 130.2(A)(2).")
        resultado = texto(detalle, RESULTADO_ARCO).casefold()
        if "requiere evaluación" in resultado or "método no aplicable" in resultado:
            faltantes.append("Completa el resultado de arco con una evaluación documentada aplicable.")
        riesgo_id = texto(detalle, "Referencia de evaluación de riesgos")
        if riesgos is not None and es_id(riesgo_id) and riesgo_id not in riesgos:
            faltantes.append("La evaluación de riesgos indicada no está disponible en este proyecto.")
        referencia = texto(detalle, "Referencia de evaluación de arco")
        if puntos is not None and referencia in puntos:
            punto = puntos[referencia]
            if not resultado_arco_vigente(punto):
                faltantes.append("El punto vinculado requiere revisión en el módulo 4.")
            elif texto(detalle, "Referencia y revisión del análisis técnico") != revision_punto(punto):
                faltantes.append("Actualiza la revisión del punto vinculado en el permiso.")
            else:
                esperados = {
                    "Equipo": texto(punto, "Equipo"),
                    "Ubicación": texto(punto, "Ubicación"),
                    RESULTADO_ARCO: f"Categoría {punto['Categoría']} según el método de tablas",
                    FRONTERA: f"{punto['Frontera de arco']} m"
                }
                for campo, esperado in esperados.items():
                    if texto(detalle, campo).casefold() != esperado.casefold():
                        faltantes.append(f"{campo}: debe coincidir con el punto vinculado.")
        elif puntos is not None and es_id(referencia):
            faltantes.append("El punto indicado no está disponible en este proyecto.")
    else:
        referencia = texto(detalle, "Referencia del procedimiento LOTO")
        identificador = referencia.rsplit(" | ", 1)[-1]
        if procedimientos is not None and es_id(identificador) and identificador not in procedimientos:
            faltantes.append("El procedimiento LOTO indicado no está disponible en este proyecto.")
    return list(dict.fromkeys(faltantes))


def es_id(valor):
    from uuid import UUID
    try:
        UUID(valor)
    except ValueError:
        return False
    return True


def revision_punto(detalle):
    return f"{detalle.get('Código del punto', '')} · revisión {detalle.get('Revisión', 'sin revisión')}"


def recuperar(tabla, proyecto, etiqueta, nombre, filtrar=None):
    registros = consultar(tabla, {"proyecto_id": proyecto["id"]})
    opciones = {}
    for registro in registros:
        detalle = registro.get("detalle") or {}
        if filtrar is None or detalle.get("Tipo") == filtrar:
            opciones[str(registro["id"])] = {
                **detalle, "_nombre": detalle.get(nombre) or registro.get("nombre") or etiqueta
            }
    seleccion = st.selectbox(
        etiqueta, [None, *opciones],
        format_func=lambda x: "Sin vínculo" if x is None else f"{opciones[x]['_nombre']} | {x[:8]}",
        key=f"permiso_{tabla}_{proyecto['id']}"
    )
    return seleccion, opciones


def mostrar():
    st.title("07. Permisos de trabajo eléctrico")
    advertencia_tecnica()
    proyecto = seleccionar_proyecto("permisos")
    if not proyecto:
        return

    registros = consultar("permisos", {"proyecto_id": proyecto["id"]})
    tipo = st.radio("Tipo de permiso", ["Trabajo energizado", "Trabajo desenergizado"],
                    horizontal=True, key=f"tipo_permiso_{proyecto['id']}")
    energizado = tipo == "Trabajo energizado"
    inicial = {}
    puntos = procedimientos = riesgos = None
    st.caption("Guarda el borrador antes de cambiar el tipo, el proyecto o los documentos vinculados.")
    if energizado:
        st.info("Planificación y permiso académico según 110.3(I) y 130.3. Anexos I y J informativos.")
        riesgo_id, riesgos = recuperar("evaluaciones", proyecto, "Evaluación de riesgos del módulo 3", "nombre")
        arco_id, puntos = recuperar("arco_electrico", proyecto, "Punto de análisis del módulo 4", "Equipo")
        if riesgo_id:
            inicial["Referencia de evaluación de riesgos"] = riesgo_id
        if arco_id:
            punto = puntos[arco_id]
            inicial.update({
                "Equipo": texto(punto, "Equipo"),
                "Ubicación": texto(punto, "Ubicación"),
                "Referencia de evaluación de arco": arco_id,
                "Referencia y revisión del análisis técnico": revision_punto(punto),
                "Tensión nominal": f"{texto(punto, 'Tensión (V)')} V {texto(punto, 'Sistema')}",
                "Tensión de exposición al choque": (
                    f"{texto(punto, 'Tensión de exposición (V)')} V {texto(punto, 'Sistema')}"
                    if punto.get("Tensión de exposición (V)") else ""
                ),
                "Límite de aproximación limitada": texto(punto, "Aproximación limitada"),
                "Límite de aproximación restringida": texto(punto, "Aproximación restringida")
            })
            if resultado_arco_vigente(punto):
                inicial[RESULTADO_ARCO] = f"Categoría {punto['Categoría']} según el método de tablas"
                inicial[FRONTERA] = f"{punto['Frontera de arco']} m"
            else:
                st.warning("El punto vinculado requiere revisión antes de reutilizar sus resultados de arco.")
                inicial[RESULTADO_ARCO] = "Método no aplicable. Requiere evaluación."
        campos = ENERGIZADO
        referencia = "NFPA 70E 2027: 110.2(B), 110.3(I), 130.2 a 130.5. Anexos I y J informativos."
        titulo = "Permiso de trabajo eléctrico energizado"
    else:
        st.info("Formulario interno académico para planificar la condición de trabajo eléctricamente segura y documentar el cierre.")
        loto_id, procedimientos = recuperar("loto", proyecto, "Procedimiento LOTO del proyecto",
                                            "Identificación", "Política LOTO")
        if loto_id:
            inicial["Referencia del procedimiento LOTO"] = f"{procedimientos[loto_id]['_nombre']} | {loto_id}"
        campos = DESENERGIZADO
        referencia = "NFPA 70E 2027: 110.3(I), 120.2 a 120.6. Anexos G e I informativos."
        titulo = "Permiso interno de trabajo desenergizado"

    def validar(detalle):
        return validar_permiso(detalle, energizado, puntos, procedimientos, riesgos)

    propios = [r.get("detalle") or {} for r in registros if (r.get("detalle") or {}).get("Tipo") == tipo]
    estados = [estado_documental(detalle, validar) for detalle in propios]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Permisos", len(propios))
    c2.metric("En revisión", estados.count("Pendiente de revisión") + estados.count("Revisado"))
    c3.metric("Aprobación académica", estados.count("Aprobado"))
    c4.metric("Rechazados", estados.count("Rechazado"))

    administrar_documentos(
        "permisos", proyecto, titulo, campos, referencia, inicial=inicial, tipo=tipo,
        validar=validar, opciones_campos=OPCIONES_ENERGIZADO if energizado else None,
        ayudas=AYUDAS, registros=registros
    )
