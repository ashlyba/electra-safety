
import streamlit as st

from modules import proteccion_personal
from modules import expediente


def mostrar():

    st.title("Centro de consulta técnica")

    st.caption(
        "Recursos complementarios de Electra Safe 360."
    )

    recurso = st.radio(
        "Seleccionar herramienta",
        [
            "Protección personal",
            "Expediente del proyecto"
        ],
        horizontal=True
    )

    st.divider()

    if recurso == "Protección personal":

        proteccion_personal.mostrar()

    else:

        expediente.mostrar()
