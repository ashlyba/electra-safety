
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


def valor(detalle, campo):

    resultado = detalle.get(campo)

    if resultado is None or resultado == "":
        return ""

    return str(resultado)


def mostrar():

    st.title("07. Permisos de trabajo eléctrico")

    st.write(
        "Preparación, revisión, control documental "
        "e impresión de permisos de trabajo eléctrico."
    )

    advertencia_tecnica()

    proyecto = seleccionar_proyecto("permisos")

    if not proyecto:
        return

    registros = consultar(
        "permisos",
        {"proyecto_id": proyecto["id"]}
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Permisos", len(registros))

    c2.metric(
        "En revisión",
        sum(
            (r.get("detalle") or {}).get("Estado")
            in ["Pendiente de revisión", "Revisado"]
            for r in registros
        )
    )

    c3.metric(
        "Aprobados",
        sum(
            (r.get("detalle") or {}).get("Estado")
            == "Aprobado"
            for r in registros
        )
    )

    c4.metric(
        "Rechazados",
        sum(
            (r.get("detalle") or {}).get("Estado")
            == "Rechazado"
            for r in registros
        )
    )

    st.divider()

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
            "El trabajo energizado requiere justificación "
            "y evaluación técnica. Este formulario no "
            "autoriza automáticamente su ejecución."
        )

        evaluaciones = consultar(
            "evaluaciones",
            {"proyecto_id": proyecto["id"]}
        )

        opciones_riesgos = {
            r["id"]: r for r in evaluaciones
        }

        riesgo_id = st.selectbox(
            "Vincular evaluación de riesgos del módulo 3",
            [None] + list(opciones_riesgos),
            format_func=lambda x: (
                "Sin evaluación vinculada"
                if x is None
                else str(
                    (opciones_riesgos[x].get("detalle") or {})
                    .get("Identificación", "Evaluación")
                ) + " | " + str(x)[:8]
            ),
            key="permiso_riesgo"
        )

        if riesgo_id:

            inicial["Referencia de evaluación de riesgos"] = (
                str(riesgo_id)
            )

        registros_arco = consultar(
            "arco_electrico",
            {"proyecto_id": proyecto["id"]}
        )

        opciones = {
            r["id"]: r for r in registros_arco
        }

        seleccion = st.selectbox(
            "Recuperar evaluación del módulo 4",
            [None] + list(opciones),
            format_func=lambda x: (
                "Sin evaluación vinculada"
                if x is None
                else str(
                    (opciones[x].get("detalle") or {})
                    .get("Equipo", "Evaluación")
                ) + " | " + str(x)[:8]
            ),
            key="permiso_arco"
        )

        if seleccion:

            detalle = opciones[seleccion].get("detalle") or {}

            aplicable = detalle.get("Método aplicable") == "Sí"

            tension = valor(detalle, "Tensión (V)")

            frontera = valor(detalle, "Frontera de arco")

            inicial.update({
                "Equipo": valor(detalle, "Equipo"),
                "Ubicación": valor(detalle, "Ubicación"),
                "Referencia de evaluación de arco": str(seleccion),
                "Tensión nominal": (
                    f"{tension} V {valor(detalle, 'Sistema')}"
                    if tension else ""
                ),
                "Resultado de evaluación de arco": (
                    "Categoría " + valor(detalle, "Categoría")
                    if aplicable
                    else "Método no aplicable. Requiere evaluación."
                ),
                "Frontera de arco eléctrico": (
                    frontera + " m"
                    if frontera and aplicable
                    else ""
                ),
                "Límite de aproximación limitada":
                    valor(detalle, "Aproximación limitada"),
                "Límite de aproximación restringida":
                    valor(detalle, "Aproximación restringida")
            })

            if not aplicable:

                st.warning(
                    "La evaluación vinculada no confirma "
                    "la aplicabilidad del método de categorías."
                )

        if "permiso_energizado_vinculo" not in st.session_state:

            st.session_state[
                "permiso_energizado_vinculo"
            ] = (riesgo_id, seleccion)

        vinculo = (riesgo_id, seleccion)

        if st.session_state[
            "permiso_energizado_vinculo"
        ] != vinculo:

            for clave in list(st.session_state):

                if (
                    clave.startswith(
                        f"permisos_{tipo}_{proyecto['id']}_nuevo_"
                    )
                ):

                    del st.session_state[clave]

            st.session_state[
                "permiso_energizado_vinculo"
            ] = vinculo

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

        st.info(
            "Formulario interno para documentar "
            "la planificación, verificación y ejecución "
            "de trabajos desenergizados."
        )

        registros_loto = consultar(
            "loto",
            {"proyecto_id": proyecto["id"]}
        )

        registros_loto = [
            r for r in registros_loto
            if (r.get("detalle") or {}).get("Tipo")
            == "Política LOTO"
        ]

        opciones = {
            r["id"]: r for r in registros_loto
        }

        seleccion = st.selectbox(
            "Vincular procedimiento LOTO",
            [None] + list(opciones),
            format_func=lambda x: (
                "Sin procedimiento vinculado"
                if x is None
                else str(
                    (opciones[x].get("detalle") or {})
                    .get("Identificación", "Procedimiento")
                ) + " | " + str(x)[:8]
            ),
            key="permiso_loto"
        )

        if seleccion:

            d = opciones[seleccion].get("detalle") or {}

            inicial = {
                "Referencia del procedimiento LOTO": (
                    str(d.get("Identificación", ""))
                    + " | "
                    + str(seleccion)
                )
            }

            st.caption(
                "Estado del procedimiento vinculado: "
                + str(d.get("Estado", "Borrador"))
            )

        if st.session_state.get(
            "permiso_desenergizado_vinculo"
        ) != seleccion:

            for clave in list(st.session_state):

                if clave.startswith(
                    f"permisos_{tipo}_{proyecto['id']}_nuevo_"
                ):

                    del st.session_state[clave]

            st.session_state[
                "permiso_desenergizado_vinculo"
            ] = seleccion

        administrar_documentos(
            "permisos",
            proyecto,
            "Permiso interno de trabajo desenergizado",
            DESENERGIZADO,
            "NFPA 70E 2027, artículo 120.",
            inicial=inicial,
            tipo=tipo
        )
