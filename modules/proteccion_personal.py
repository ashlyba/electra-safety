
import streamlit as st
import pandas as pd

from database import consultar
from modules.comunes import seleccionar_proyecto
from modules.guia_epp import mostrar_guia_epp


def mostrar():

    st.title("Equipos de protección personal")

    st.caption(
        "Consulta de evaluaciones y selección "
        "documentada de equipos de protección."
    )

    proyecto = seleccionar_proyecto("proteccion")

    if not proyecto:
        return

    tab1, tab2 = st.tabs([
        "Evaluaciones del proyecto",
        "Guía de protección personal"
    ])

    with tab1:

        registros = consultar(
            "arco_electrico",
            {"proyecto_id": proyecto["id"]}
        )

        if not registros:

            st.info(
                "No existen evaluaciones de arco "
                "eléctrico registradas para este proyecto."
            )

        else:

            opciones = {
                r["id"]: r for r in registros
            }

            seleccion = st.selectbox(
                "Seleccionar equipo evaluado",
                list(opciones),
                format_func=lambda x: (
                    str(
                        opciones[x].get("detalle", {}).get(
                            "Equipo", "Equipo"
                        )
                    )
                    + " | " + str(x)[:8]
                )
            )

            detalle = (
                opciones[seleccion].get("detalle")
                or {}
            )

            c1, c2 = st.columns(2)

            with c1:

                st.write(
                    "**Equipo:**",
                    detalle.get("Equipo", "No registrado")
                )

                st.write(
                    "**Ubicación:**",
                    detalle.get("Ubicación", "No registrada")
                )

            with c2:

                st.write(
                    "**Sistema:**",
                    detalle.get("Sistema", "No registrado")
                )

                st.write(
                    "**Tensión nominal:**",
                    detalle.get("Tensión (V)", "No registrada")
                )

            st.divider()

            if detalle.get("Método aplicable") == "Sí":

                st.metric(
                    "Categoría registrada",
                    detalle.get("Categoría", "No registrada")
                )

                st.warning(
                    "Resultado académico pendiente "
                    "de validación técnica."
                )

            else:

                st.warning(
                    "No se dispone de una categoría "
                    "aplicable mediante el método "
                    "de tablas implementado."
                )

            st.subheader(
                "Información de la evaluación"
            )

            st.dataframe(
                pd.DataFrame([
                    {
                        "Parámetro": campo,
                        "Resultado": str(valor)
                    }
                    for campo, valor in detalle.items()
                ]),
                hide_index=True,
                use_container_width=True
            )

    with tab2:

        mostrar_guia_epp()
