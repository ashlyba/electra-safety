
import streamlit as st
from pathlib import Path

# CONFIGURACIÓN GENERAL

st.set_page_config(
    page_title="Electra Safety | Maletín Digital",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOGO = BASE_DIR / "logo.png"

# IDENTIDAD VISUAL

st.markdown("""
<style>
    .stApp {
        background-color: #F5F5F5;
    }

    [data-testid="stSidebar"] {
        background-color: #0C2335;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #0C2335;
    }

    .banner {
        background-color: #0C2335;
        padding: 32px;
        border-radius: 14px;
        border-left: 8px solid #FFB900;
        margin-bottom: 24px;
    }

    .banner h1 {
        color: #FFFFFF;
        margin: 0;
    }

    .banner p {
        color: #E2E8F0;
    }

    .modulo {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border-top: 4px solid #FFB900;
        min-height: 155px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px #0000000D;
    }

    .modulo h3 {
        font-size: 19px;
        margin-top: 0;
    }

    .modulo p {
        color: #526575;
        font-size: 14px;
    }

    .stButton > button {
        border-radius: 8px;
        border: 1px solid #FFB900;
        font-weight: 600;
        width: 100%;
    }

    .pie {
        color: #64748B;
        font-size: 12px;
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# MÓDULOS DEL MALETÍN

modulos = {
    "Inicio": "Panel principal",
    "01. Clientes": "Registro y administración de clientes.",
    "02. Proyectos": "Creación y seguimiento de proyectos.",
    "03. Riesgos eléctricos": "Evaluación de peligros, riesgos y controles.",
    "04. Arco eléctrico y EPP": "Categorías de EPP y fronteras de protección.",
    "05. Etiquetas": "Generación de etiquetas de seguridad eléctrica.",
    "06. Bloqueo y etiquetado LOTO": "Gestión del control de energías peligrosas.",
    "07. Permisos de trabajo": "Permisos de trabajo energizado y desenergizado."
}

def navegar(destino):
    st.session_state["pagina"] = destino

# MENÚ LATERAL

with st.sidebar:

    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    else:
        st.header("Electra Safety")

    st.markdown("### Maletín digital")
    st.caption("Seguridad eléctrica | NFPA 70E 2027")

    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        list(modulos.keys()),
        key="pagina"
    )

    st.divider()

    st.caption("ElectraSafety Consultores")
    st.caption("Versión 0.1 | Desarrollo académico")

# PANTALLA PRINCIPAL

if pagina == "Inicio":

    st.markdown("""
    <div class="banner">
        <h1>Electra Safe 360</h1>
        <p>Maletín digital de herramientas para la gestión
        de la seguridad eléctrica.</p>
        <p>NFPA 70E | Edición 2027</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Panel general")

    c1, c2, c3 = st.columns(3)

    c1.metric("Módulos disponibles", "7")
    c2.metric("Edición normativa", "2027")
    c3.metric("Versión", "0.1")

    st.info(
        "Aplicación académica en desarrollo. "
        "Las herramientas técnicas serán habilitadas "
        "después de su implementación y validación."
    )

    st.divider()

    st.subheader("Herramientas de seguridad eléctrica")

    herramientas = list(modulos.items())[1:]

    for i in range(0, len(herramientas), 3):

        columnas = st.columns(3)

        for columna, (nombre, descripcion) in zip(
            columnas, herramientas[i:i+3]
        ):
            with columna:

                st.markdown(
                    f"""
                    <div class="modulo">
                        <h3>{nombre}</h3>
                        <p>{descripcion}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.button(
                    "Abrir herramienta",
                    key=f"btn_{nombre}",
                    on_click=navegar,
                    args=(nombre,)
                )

    st.divider()

    st.subheader("Acerca del maletín")

    st.write(
        "Electra Safe 360 es una herramienta digital "
        "desarrollada para apoyar la evaluación y gestión "
        "de la seguridad eléctrica en los lugares de trabajo."
    )

    st.write(
        "Referencia normativa: NFPA 70E, edición 2027."
    )

    with st.expander("Equipo de desarrollo"):

        st.write("Integrante 1: Pendiente")
        st.write("Integrante 2: Pendiente")
        st.write("Integrante 3: Pendiente")
        st.write("Integrante 4: Pendiente")

    with st.expander("Herramientas utilizadas"):

        st.write("Inteligencia artificial: ChatGPT.")
        st.write("Lenguaje de programación: Python.")
        st.write("Interfaz: Streamlit.")
        st.write("Control de versiones: GitHub.")

# PÁGINAS DE LOS MÓDULOS

else:

    st.title(pagina)
    st.write(modulos[pagina])

    st.divider()

    st.warning(
        "Este módulo se encuentra en desarrollo. "
        "Todavía no genera resultados técnicos."
    )

    st.button(
        "Volver al inicio",
        on_click=navegar,
        args=("Inicio",)
    )

# PIE DE PÁGINA

st.markdown("""
<div class="pie">
    ElectraSafety Consultores |
    Electra Safe 360 |
    Proyecto académico de Seguridad Eléctrica
</div>
""", unsafe_allow_html=True)
