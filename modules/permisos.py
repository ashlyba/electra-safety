
import streamlit as st

from database import consultar

from modules.comunes import (
    seleccionar_proyecto,
    advertencia_tecnica
)

from modules.documentos import administrar_documentos


ENERGIZADO = {
    "1. Identificación del trabajo": [
        "Identificación",
        "Equipo",
        "Ubicación",
        "Fecha y horario",
        "Descripción y alcance de la tarea"
    ],
    "2. Justificación y necesidad del permiso": [
        "Justificación del trabajo energizado",
        "Evaluación de necesidad del permiso",
        "Excepción aplicable y fundamento"
    ],
    "3. Evaluaciones técnicas": [
        "Referencia de evaluación de riesgos",
        "Referencia de evaluación de arco",
        "Tensión nominal",
        "Resultado de evaluación de choque",
        "Resultado de evaluación de arco",
        "Frontera de arco eléctrico",
        "Límite de aproximación limitada",
        "Límite de aproximación restringida",
        "EPP requerido"
    ],
    "4. Medidas de protección": [
        "Prácticas de trabajo",
        "Herramientas y equipos",
        "Delimitación del área",
        "Control de acceso",
        "Condiciones de suspensión"
    ],
    "5. Personal y planificación": [
        "Personal calificado",
        "Competencias y funciones",
        "Reunión informativa previa",
        "Previsiones de emergencia",
        "Medios de comunicación y rescate"
    ],
    "6. Revisión y aprobación": [
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
        "Descripción y alcance de la tarea"
    ],
    "2. Identificación y aislamiento": [
        "Fuentes de energía",
        "Puntos de aislamiento",
        "Dispositivos de aislamiento",
        "Referencia del procedimiento LOTO",
        "Participantes",
        "Candados y etiquetas"
    ],
    "3. Condición eléctricamente segura": [
        "Tratamiento de energía almacenada",
        "Instrumento de verificación",
        "Comprobación del instrumento",
        "Verificación de ausencia de tensión",
        "Resultados de la verificación",
        "Responsable de verificación",
        "Liberación documentada para trabajar"
    ],
    "4. Ejecución del trabajo": [
        "Medidas de protección",
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


def mostrar():

    st.title("07. Permisos de trabajo eléctrico")

    advertencia_tecnica()

    proyecto = seleccionar_proyecto("permisos")

    if not proyecto:
        return

    tipo = st.radio(
        "Tipo de permiso",
        [
            "Trabajo energizado",
            "Trabajo desenergizado"
        ],
        horizontal=True
    )

    inicial = {}

    if tipo == "Trabajo energizado":

        st.warning(
            "El formulario no autoriza automáticamente "
            "la realización de trabajo energizado."
        )

        registros = consultar(
            "arco_electrico",
            {"proyecto_id": proyecto["id"]}
        )

        opciones = {
            r["id"]: r for r in registros
        }

        seleccion = st.selectbox(
            "Recuperar evaluación del módulo 4",
            [None] + list(opciones),
            format_func=lambda x: (
                "Sin evaluación vinculada"
                if x is None
                else opciones[x].get("detalle", {}).get(
                    "Equipo", "Evaluación"
                ) + " | " + str(x)[:8]
            )
        )

        if seleccion:

            detalle = opciones[seleccion].get("detalle") or {}

            inicial = {
                "Equipo": detalle.get("Equipo"),
                "Ubicación": detalle.get("Ubicación"),
                "Referencia de evaluación de arco": seleccion,
                "Tensión nominal": (
                    f"{detalle.get('Tensión (V)')} "
                    f"V {detalle.get('Sistema')}"
                ),
                "Resultado de evaluación de arco": (
                    "Categoría " + str(detalle.get("Categoría"))
                    if detalle.get("Método aplicable") == "Sí"
                    else "Método no aplicable"
                ),
                "Frontera de arco eléctrico": (
                    str(detalle.get("Frontera de arco")) + " m"
                    if detalle.get("Frontera de arco") is not None
                    else "Pendiente de evaluación"
                ),
                "Límite de aproximación limitada":
                    detalle.get("Aproximación limitada"),
                "Límite de aproximación restringida":
                    detalle.get("Aproximación restringida")
            }

        administrar_documentos(
            "permisos",
            proyecto,
            "Permiso de trabajo eléctrico energizado",
            ENERGIZADO,
            "NFPA 70E 2027, artículos 110 y 130.",
            inicial=inicial,
            tipo=tipo
        )

    else:

        registros = consultar(
            "loto",
            {"proyecto_id": proyecto["id"]}
        )

        opciones = {
            r["id"]: r for r in registros
        }

        seleccion = st.selectbox(
            "Vincular procedimiento LOTO",
            [None] + list(opciones),
            format_func=lambda x: (
                "Sin procedimiento vinculado"
                if x is None
                else opciones[x].get("detalle", {}).get(
                    "Identificación", "Procedimiento"
                ) + " | " + str(x)[:8]
            )
        )

        if seleccion:

            inicial = {
                "Referencia del procedimiento LOTO": seleccion
            }

        administrar_documentos(
            "permisos",
            proyecto,
            "Permiso interno de trabajo desenergizado",
            DESENERGIZADO,
            "NFPA 70E 2027, artículo 120.",
            inicial=inicial,
            tipo=tipo
        )
