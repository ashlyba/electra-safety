
import streamlit as st
import pandas as pd


CLASIFICACIONES = {
    1: 4,
    2: 8,
    3: 25,
    4: 40
}


COMPONENTES = [
    ("Cabeza", "Casco de seguridad"),
    ("Ojos", "Protección ocular"),
    ("Rostro", "Pantalla facial o capucha"),
    ("Oídos", "Protección auditiva"),
    ("Torso", "Ropa con clasificación contra arco"),
    ("Brazos", "Protección de brazos"),
    ("Manos", "Guantes y protectores"),
    ("Piernas", "Ropa de protección"),
    ("Pies", "Calzado de seguridad")
]


def mostrar_ilustracion():

    st.html("""
    <svg viewBox="0 0 440 450"
         width="100%"
         xmlns="http://www.w3.org/2000/svg">

        <rect width="440" height="450"
              rx="12" fill="#F2F5F8"/>

        <g stroke="#0D2333" stroke-width="3">

            <circle cx="220" cy="70"
                    r="35" fill="#CBD5E1"/>

            <path d="M180 65 Q220 0 260 65 Z"
                  fill="#FFB800"/>

            <rect x="191" y="70"
                  width="58" height="28"
                  rx="5" fill="#9BB6C8"/>

            <rect x="205" y="104"
                  width="30" height="25"
                  fill="#CBD5E1"/>

            <path d="M175 128 L265 128
                     L280 265 L160 265 Z"
                  fill="#294758"/>

            <path d="M175 128 L125 220
                     L150 238 L195 150 Z"
                  fill="#294758"/>

            <path d="M265 128 L315 220
                     L290 238 L245 150 Z"
                  fill="#294758"/>

            <rect x="122" y="220"
                  width="30" height="40"
                  rx="8" fill="#FFB800"/>

            <rect x="288" y="220"
                  width="30" height="40"
                  rx="8" fill="#FFB800"/>

            <path d="M160 265 L215 265
                     L205 395 L160 395 Z"
                  fill="#294758"/>

            <path d="M225 265 L280 265
                     L280 395 L235 395 Z"
                  fill="#294758"/>

            <rect x="148" y="395"
                  width="62" height="26"
                  rx="5" fill="#0D2333"/>

            <rect x="232" y="395"
                  width="62" height="26"
                  rx="5" fill="#0D2333"/>

        </g>

        <g stroke="#64748B"
           stroke-width="1.5">

            <path d="M185 45 H80"/>
            <path d="M249 80 H360"/>
            <path d="M170 165 H70"/>
            <path d="M318 240 H380"/>
            <path d="M280 330 H360"/>
            <path d="M148 410 H80"/>

        </g>

        <g fill="#0D2333"
           font-family="Arial"
           font-size="12">

            <text x="20" y="38">Cabeza</text>
            <text x="300" y="73">Rostro y ojos</text>
            <text x="15" y="158">Torso y brazos</text>
            <text x="330" y="232">Manos</text>
            <text x="315" y="323">Piernas</text>
            <text x="30" y="402">Pies</text>

        </g>

    </svg>
    """)

    st.caption(
        "Esquema ilustrativo de protección corporal. "
        "No representa un conjunto certificado."
    )


def mostrar_guia_epp(
    categoria=None,
    clave="guia_epp"
):

    st.subheader(
        "Equipos de protección personal"
    )

    st.caption(
        "Referencia académica: NFPA 70E 2027."
    )

    if categoria not in CLASIFICACIONES:

        categoria = st.selectbox(
            "Categoría de protección",
            [1, 2, 3, 4],
            key=f"{clave}_categoria"
        )

    requerida = CLASIFICACIONES[categoria]

    c1, c2 = st.columns([1, 1.5])

    with c1:

        mostrar_ilustracion()

    with c2:

        st.metric(
            "Categoría de EPP",
            categoria
        )

        st.metric(
            "Clasificación mínima contra arco",
            f"{requerida} cal/cm²"
        )

        seleccionada = st.number_input(
            "Clasificación del conjunto "
            "seleccionado (cal/cm²)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"{clave}_clasificacion"
        )

        if seleccionada == 0:

            st.info(
                "Ingrese la clasificación indicada "
                "por el fabricante."
            )

        elif seleccionada < requerida:

            st.error(
                "Clasificación inferior al mínimo "
                "correspondiente a la categoría."
            )

        else:

            st.success(
                "La clasificación ingresada "
                "alcanza el mínimo numérico."
            )

            st.caption(
                "Esto no demuestra por sí solo "
                "la conformidad del conjunto."
            )

    st.divider()

    st.subheader(
        "Verificación de componentes"
    )

    st.dataframe(
        pd.DataFrame(
            COMPONENTES,
            columns=[
                "Zona corporal",
                "Elemento de protección"
            ]
        ),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Los componentes obligatorios deben "
        "determinarse según la categoría, "
        "las notas y las condiciones normativas."
    )

    for zona, elemento in COMPONENTES:

        st.checkbox(
            f"Verificación documental: {elemento}",
            key=f"{clave}_{zona}"
        )

    st.text_area(
        "Fabricante, modelo, certificación "
        "y observaciones",
        key=f"{clave}_observaciones"
    )

    st.warning(
        "La protección contra arco eléctrico "
        "no equivale a aislamiento dieléctrico. "
        "Ambos riesgos deben evaluarse por separado."
    )

    st.caption(
        "Herramienta académica. No constituye "
        "una autorización de trabajo."
    )


def mostrar():

    mostrar_guia_epp()
