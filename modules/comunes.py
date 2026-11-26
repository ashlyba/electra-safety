
import streamlit as st
import logging

from database import consultar


MODULOS_TECNICOS = {
    "evaluaciones": "Riesgos eléctricos",
    "arco_electrico": "Arco eléctrico y EPP",
    "etiquetas": "Etiquetas eléctricas",
    "loto": "Bloqueo y etiquetado LOTO",
    "permisos": "Permisos de trabajo"
}


def seleccionar_proyecto(clave):

    try:

        proyectos = consultar("proyectos")

        clientes = {
            c["id"]: c["nombre_empresa"]
            for c in consultar("clientes")
        }

    except Exception:

        logging.exception(
            "Error al consultar proyectos"
        )

        st.error(
            "No fue posible recuperar los proyectos."
        )

        return None

    if not proyectos:

        st.warning(
            "Debe registrar un cliente y un proyecto "
            "antes de utilizar esta herramienta."
        )

        return None

    opciones = {
        p["id"]: p
        for p in proyectos
    }

    ids = list(opciones)

    activo = st.session_state.get(
        "proyecto_activo"
    )

    if activo not in ids:

        activo = ids[0]

        st.session_state[
            "proyecto_activo"
        ] = activo

    widget = f"proyecto_{clave}"

    st.session_state[widget] = activo

    def cambiar_proyecto():

        st.session_state[
            "proyecto_activo"
        ] = st.session_state[widget]

    seleccionado = st.selectbox(
        "Proyecto de trabajo",
        ids,
        format_func=lambda x: (
            clientes.get(
                opciones[x]["cliente_id"],
                "Cliente"
            )
            + " | "
            + opciones[x]["nombre"]
        ),
        key=widget,
        on_change=cambiar_proyecto
    )

    proyecto = opciones[seleccionado]

    with st.container(border=True):

        c1, c2 = st.columns([2, 1])

        with c1:

            st.caption("CLIENTE")

            st.write(
                clientes.get(
                    proyecto["cliente_id"],
                    "No registrado"
                )
            )

        with c2:

            st.caption("CÓDIGO DEL PROYECTO")

            st.write(
                proyecto.get("codigo", "")
            )

    st.caption(
        "Guarde los cambios antes de seleccionar "
        "otro proyecto."
    )

    return proyecto


def obtener_avance(proyecto_id):

    resultados = []

    for tabla, nombre in MODULOS_TECNICOS.items():

        registros = consultar(
            tabla,
            {"proyecto_id": proyecto_id}
        )

        resultados.append({
            "Módulo": nombre,
            "Registros": len(registros),
            "Estado": (
                "Con registros"
                if registros
                else "Sin iniciar"
            )
        })

    iniciados = sum(
        r["Registros"] > 0
        for r in resultados
    )

    porcentaje = round(
        iniciados / len(MODULOS_TECNICOS) * 100
    )

    return porcentaje, resultados


def mostrar_avance(
    proyecto_id,
    compacto=False
):

    try:

        porcentaje, resultados = obtener_avance(
            proyecto_id
        )

    except Exception:

        logging.exception(
            "Error al calcular avance"
        )

        st.caption(
            "Avance temporalmente no disponible."
        )

        return

    st.caption("AVANCE DOCUMENTAL")

    st.progress(porcentaje / 100)

    st.write(
        f"{porcentaje}% de módulos iniciados"
    )

    if not compacto:

        st.dataframe(
            resultados,
            hide_index=True,
            use_container_width=True
        )

        st.caption(
            "El indicador representa la existencia "
            "de registros y no la aprobación "
            "técnica del proyecto."
        )


def notificar(clave, mensaje):

    st.session_state[
        f"aviso_{clave}"
    ] = mensaje

    st.rerun()


def mostrar_aviso(clave):

    mensaje = st.session_state.pop(
        f"aviso_{clave}",
        None
    )

    if mensaje:

        st.success(mensaje)


def advertencia_tecnica():

    st.caption(
        "Herramienta académica de apoyo. "
        "Los resultados requieren revisión por "
        "personal calificado antes de su "
        "aplicación real."
    )
