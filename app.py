
import streamlit as st

from pathlib import Path
from database import (
    conectar,
    iniciar_sesion,
    cerrar_sesion,
    consultar,
    contar
)

from modules import clientes, proyectos


st.set_page_config(
    page_title="Electra Safety | Maletín Digital",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOGO = BASE_DIR / "logo.png"


# DISEÑO CORPORATIVO

st.markdown("""
<style>

.stApp {
    background-color: #F5F5F5;
}

[data-testid="stSidebar"] {
    background-color: #0C2335;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: #FFFFFF;
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2rem;
}

.banner {
    background: #0C2335;
    border-left: 8px solid #FFB900;
    padding: 28px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.banner-titulo {
    font-size: 34px;
    font-weight: 750;
    color: #FFFFFF !important;
    margin-bottom: 10px;
}

.banner-subtitulo {
    color: #E2E8F0 !important;
    font-size: 16px;
}

.banner-norma {
    color: #FFB900 !important;
    font-weight: 600;
    font-size: 14px;
    margin-top: 14px;
}

.modulo {
    background: #FFFFFF;
    border-top: 4px solid #FFB900;
    border-radius: 10px;
    padding: 18px;
    min-height: 170px;
    margin-top: 8px;
    box-shadow: 0 2px 6px #0000000D;
}

.modulo-titulo {
    color: #0C2335;
    font-size: 18px;
    font-weight: 700;
}

.modulo p {
    color: #526575;
    font-size: 14px;
}

.estado-activo {
    color: #18754A;
    font-size: 12px;
    font-weight: 600;
}

.estado-pendiente {
    color: #8C6500;
    font-size: 12px;
    font-weight: 600;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
}

.pie {
    text-align: center;
    font-size: 12px;
    color: #64748B;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# INICIO DE SESIÓN

if "usuario" not in st.session_state:

    izquierda, centro, derecha = st.columns([1, 2, 1])

    with centro:

        if LOGO.exists():
            st.image(str(LOGO), use_container_width=True)

        st.title("Electra Safe 360")

        st.write(
            "Maletín digital de seguridad eléctrica"
        )

        with st.form("login"):

            correo = st.text_input("Correo electrónico")

            password = st.text_input(
                "Contraseña",
                type="password"
            )

            entrar = st.form_submit_button(
                "Iniciar sesión",
                type="primary",
                use_container_width=True
            )

            if entrar:

                try:
                    if iniciar_sesion(correo, password):
                        st.rerun()
                    else:
                        st.error("No se pudo iniciar sesión.")

                except Exception:
                    st.error(
                        "No se pudo iniciar sesión. "
                        "Verifica tus credenciales y la conexión."
                    )

        st.caption(
            "ElectraSafety Consultores | NFPA 70E 2027"
        )

    st.stop()


# DEFINICIÓN DE MÓDULOS

modulos = {
    "Inicio": "Panel principal",
    "01. Clientes": "Registro y administración de empresas.",
    "02. Proyectos": "Creación y seguimiento de proyectos.",
    "03. Riesgos eléctricos": "Evaluación de peligros y controles.",
    "04. Arco eléctrico y EPP": "EPP y fronteras de protección.",
    "05. Etiquetas": "Etiquetas para equipos eléctricos.",
    "06. Bloqueo y etiquetado LOTO": "Control de energías peligrosas.",
    "07. Permisos de trabajo": "Gestión del trabajo eléctrico."
}

implementados = [
    "01. Clientes",
    "02. Proyectos"
]


def navegar(destino):
    st.session_state["pagina"] = destino


# MENÚ LATERAL

with st.sidebar:

    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    else:
        st.header("Electra Safety")

    st.markdown("### Maletín digital")

    st.caption("NFPA 70E | Edición 2027")

    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        list(modulos),
        key="pagina"
    )

    st.divider()

    st.markdown("### Proyecto activo")

    proyecto_id = st.session_state.get("proyecto_activo")

    if proyecto_id:

        try:
            registros = consultar(
                "proyectos",
                {"id": proyecto_id}
            )

            if registros:
                st.write(registros[0]["nombre"])
                st.caption(registros[0]["codigo"])
            else:
                st.session_state.pop("proyecto_activo", None)
                st.caption("Sin proyecto activo")

        except Exception:
            st.caption("No se pudo consultar el proyecto")

    else:
        st.caption("Sin proyecto activo")

    st.divider()

    st.caption(st.session_state.usuario)

    if st.button("Cerrar sesión"):

        try:
            cerrar_sesion()
            st.rerun()
        except Exception:
            st.error("No se pudo cerrar la sesión.")

    st.caption("Versión 0.2 | Proyecto académico")


# PANTALLA PRINCIPAL

if pagina == "Inicio":

    st.markdown("""
    <div class="banner">
        <div class="banner-titulo">
            Electra Safe 360
        </div>
        <div class="banner-subtitulo">
            Maletín digital de herramientas para
            la gestión de la seguridad eléctrica.
        </div>
        <div class="banner-norma">
            NFPA 70E | Edición 2027
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Panel general")

    try:

        total_clientes = contar("clientes")
        total_proyectos = contar("proyectos")
        total_evaluaciones = contar("riesgos") + contar(
            "arco_electrico"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Clientes", total_clientes)
        c2.metric("Proyectos", total_proyectos)
        c3.metric("Evaluaciones", total_evaluaciones)
        c4.metric("Módulos habilitados", "2 de 7")

        st.success("Conexión con la base de datos establecida.")

    except Exception:

        st.error(
            "No se pudo establecer la conexión "
            "con la base de datos."
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.button(
            "Registrar o consultar clientes",
            on_click=navegar,
            args=("01. Clientes",)
        )

    with c2:
        st.button(
            "Crear o consultar proyectos",
            on_click=navegar,
            args=("02. Proyectos",)
        )

    st.subheader("Herramientas de seguridad eléctrica")

    herramientas = list(modulos.items())[1:]

    for i in range(0, len(herramientas), 3):

        columnas = st.columns(3)

        for columna, (nombre, descripcion) in zip(
            columnas,
            herramientas[i:i+3]
        ):

            with columna:

                activo = nombre in implementados

                clase = (
                    "estado-activo"
                    if activo else "estado-pendiente"
                )

                estado = (
                    "HABILITADO"
                    if activo else "EN DESARROLLO"
                )

                st.markdown(
                    f"""
                    <div class="modulo">
                        <div class="modulo-titulo">
                            {nombre}
                        </div>
                        <p>{descripcion}</p>
                        <div class="{clase}">
                            {estado}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.button(
                    "Abrir herramienta",
                    key=f"abrir_{nombre}",
                    on_click=navegar,
                    args=(nombre,)
                )

    st.divider()

    with st.expander("Acerca del maletín"):

        st.write(
            "Electra Safe 360 es una herramienta "
            "académica de apoyo a la gestión de "
            "la seguridad eléctrica."
        )

        st.write(
            "Referencia normativa: NFPA 70E, edición 2027."
        )

        st.warning(
            "Las funciones técnicas requieren validación "
            "profesional antes de su aplicación real."
        )

    with st.expander("Equipo de desarrollo"):

        st.write("Integrante 1: Pendiente")
        st.write("Integrante 2: Pendiente")
        st.write("Integrante 3: Pendiente")
        st.write("Integrante 4: Pendiente")

    with st.expander("Herramientas utilizadas"):

        st.write("Inteligencia artificial: ChatGPT")
        st.write("Programación: Python")
        st.write("Interfaz: Streamlit")
        st.write("Base de datos: Supabase")
        st.write("Control de versiones: GitHub")


# MÓDULO 1

elif pagina == "01. Clientes":

    try:
        clientes.mostrar()
    except Exception:
        st.error(
            "No se pudo cargar el módulo de clientes. "
            "Verifica la conexión."
        )


# MÓDULO 2

elif pagina == "02. Proyectos":

    try:
        proyectos.mostrar()
    except Exception:
        st.error(
            "No se pudo cargar el módulo de proyectos. "
            "Verifica la conexión."
        )


# MÓDULOS PENDIENTES

else:

    st.title(pagina)

    st.write(modulos[pagina])

    st.warning(
        "Herramienta en desarrollo. "
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
    Seguridad Eléctrica
</div>
""", unsafe_allow_html=True)

