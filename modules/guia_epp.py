
import streamlit as st


CATEGORIAS = {
    1: 4,
    2: 8,
    3: 25,
    4: 40
}


def mostrar_guia_epp():

    st.subheader("Guía de protección personal")

    st.caption(
        "Referencia: NFPA 70E 2027, "
        "Tabla 130.7(C)(15)(c)."
    )

    categoria = st.selectbox(
        "Categoría obtenida en la evaluación",
        [1, 2, 3, 4],
        key="guia_categoria_epp"
    )

    st.metric(
        "Clasificación mínima contra arco",
        f"{CATEGORIAS[categoria]} cal/cm²"
    )

    st.warning(
        "Consulta la tabla normativa completa, "
        "incluidas sus notas y condiciones. "
        "Esta guía no sustituye la selección "
        "realizada por personal calificado."
    )

    if categoria == 1:

        st.markdown("""
- Ropa con clasificación contra arco.
- Camisa de manga larga y pantalones, u overol.
- Pantalla facial o capucha con clasificación contra arco.
        """)

    elif categoria == 2:

        st.markdown("""
- Ropa con clasificación contra arco.
- Camisa de manga larga y pantalones, u overol.
- Capucha contra arco o pantalla facial y pasamontañas
  con clasificación contra arco.
        """)

    else:

        st.markdown("""
- Consultar los requisitos específicos del traje
  y sistema de protección contra arco.
- Verificar la clasificación del conjunto completo.
- Consultar la protección requerida para cabeza,
  rostro, manos y demás partes expuestas.
        """)

    st.markdown("#### Aspectos complementarios")

    st.write(
        "Verificar los requisitos de protección "
        "ocular, auditiva, de cabeza, manos y pies "
        "establecidos para la categoría correspondiente."
    )

    st.info(
        "La protección contra choque eléctrico "
        "debe evaluarse independientemente de "
        "la protección contra arco eléctrico."
    )

    st.markdown("#### Guantes aislantes")

    st.dataframe(
        {
            "Clase": ["00", "0", "1", "2", "3", "4"],
            "Tensión máxima CA (V)": [
                500, 1000, 7500,
                17000, 26500, 36000
            ],
            "Tensión máxima CC (V)": [
                750, 1500, 11250,
                25500, 39750, 54000
            ]
        },
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Referencia: Tabla 130.7(C)(7)(a)."
    )

    st.warning(
        "Verificar tensión de exposición, protectores, "
        "estado físico, inspecciones y pruebas "
        "periódicas del equipo aislante."
    )

    st.error(
        "Material académico. No utilizar como "
        "autorización para trabajos eléctricos."
    )
