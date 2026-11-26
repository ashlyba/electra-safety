
import streamlit as st

from database import consultar


def seleccionar_proyecto(clave):

    proyectos = consultar("proyectos")

    if not proyectos:

        st.info(
            "Para comenzar, registra un cliente "
            "y crea un proyecto de trabajo."
        )

        return None

    clientes = {
        c["id"]: c["nombre_empresa"]
        for c in consultar("clientes")
    }

    opciones = {
        p["id"]: p for p in proyectos
    }

    ids = list(opciones)

    activo = st.session_state.get(
        "proyecto_activo"
    )

    if activo not in ids:
        activo = ids[0]

    widget = f"proyecto_{clave}"

    if st.session_state.get(widget) != activo:
        st.session_state[widget] = activo

    def cambiar_proyecto():

        st.session_state["proyecto_activo"] = (
            st.session_state[widget]
        )

    with st.container(border=True):

        st.caption("ESPACIO DE TRABAJO")

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

        st.session_state["proyecto_activo"] = (
            seleccionado
        )

        c1, c2 = st.columns(2)

        with c1:

            st.caption("Cliente")

            st.write(
                clientes.get(
                    proyecto["cliente_id"],
                    "No identificado"
                )
            )

        with c2:

            st.caption("Código del proyecto")

            st.write(proyecto["codigo"])

    return proyecto


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

        st.success(
            mensaje,
            icon=":material/check_circle:"
        )

        st.toast(
            mensaje,
            icon=":material/check_circle:"
        )


def advertencia_tecnica():

    st.caption(
        "Herramienta académica de apoyo. "
        "Los resultados requieren revisión por "
        "una persona calificada antes de su "
        "aplicación real."
    )
