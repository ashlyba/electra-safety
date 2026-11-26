
import streamlit as st

from database import consultar


def seleccionar_proyecto(clave):

    proyectos = consultar("proyectos")

    if not proyectos:
        st.warning(
            "Debes registrar un cliente y un proyecto "
            "antes de utilizar esta herramienta."
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

    activo = st.session_state.get("proyecto_activo")

    indice = ids.index(activo) if activo in ids else 0

    seleccionado = st.selectbox(
        "Proyecto de trabajo",
        ids,
        index=indice,
        format_func=lambda x: (
            clientes.get(
                opciones[x]["cliente_id"], ""
            )
            + " | "
            + opciones[x]["nombre"]
        ),
        key=f"proyecto_{clave}"
    )

    proyecto = opciones[seleccionado]

    st.caption(
        "Código del proyecto: " + proyecto["codigo"]
    )

    return proyecto


def notificar(clave, mensaje):

    st.session_state[f"aviso_{clave}"] = mensaje
    st.rerun()


def mostrar_aviso(clave):

    mensaje = st.session_state.pop(
        f"aviso_{clave}", None
    )

    if mensaje:
        st.success(mensaje)
        st.toast(mensaje, icon="✅")


def advertencia_tecnica():

    st.caption(
        "Herramienta académica de apoyo. "
        "Los resultados requieren revisión por una "
        "persona calificada antes de su aplicación real."
    )
