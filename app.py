
import streamlit as st
import logging

from pathlib import Path
from importlib import import_module

from database import (
    iniciar_sesion,
    cerrar_sesion,
    consultar,
    contar
)

from modules.estilos import aplicar_estilos


BASE_DIR = Path(__file__).resolve().parent
LOGO = BASE_DIR / "logo.png"

VERSION = "0.4"

st.set_page_config(
    page_title="Electra Safe 360 | ElectraSafety Consultores",
    page_icon=str(LOGO) if LOGO.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_estilos()


INTEGRANTES = [
    "Pendiente de completar"
]


MODULOS = {
    "Inicio": {
        "descripcion": "Panel general de gestión"
    },
    "01. Clientes": {
        "descripcion": (
            "Registro, consulta y administración "
            "de empresas y contactos."
        ),
        "ruta": "clientes"
    },
    "02. Proyectos": {
        "descripcion": (
            "Creación, organización y seguimiento "
            "de proyectos de seguridad eléctrica."
        ),
        "ruta": "proyectos"
    },
    "03. Riesgos eléctricos": {
        "descripcion": (
            "Identificación de peligros, valoración "
            "de riesgos y medidas de control."
        ),
        "ruta": "riesgos"
    },
    "04. Arco eléctrico y EPP": {
        "descripcion": (
            "Evaluación de arco eléctrico, choque, "
            "fronteras y equipos de protección personal."
        ),
        "ruta": "arco_electrico"
    },
    "05. Etiquetas": {
        "descripcion": (
            "Diseño, registro y generación "
            "de etiquetas de seguridad eléctrica."
        ),
        "ruta": "etiquetas"
    },
    "06. Bloqueo y etiquetado LOTO": {
        "descripcion": (
            "Control de energías peligrosas, "
            "procedimientos y dispositivos de bloqueo."
        ),
        "ruta": "loto"
    },
    "07. Permisos de trabajo": {
        "descripcion": (
            "Gestión documental de trabajos eléctricos "
            "energizados y desenergizados."
        ),
        "ruta": "permisos"
    }
}


def navegar(destino):

    st.session_state["pagina"] = destino


def mostrar_login():

    st.html("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """)

    _, centro, _ = st.columns([1, 1.5, 1])

    with centro:

        if LOGO.exists():

            st.image(
                str(LOGO),
                use_container_width=True
            )

        st.title("Electra Safe 360")

        st.write(
            "Sistema de gestión de seguridad eléctrica"
        )

        with st.form("login"):

            st.subheader("Acceso al sistema")

            correo = st.text_input(
                "Correo electrónico",
                placeholder="usuario@empresa.com"
            )

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

            if not correo.strip() or not password:

                st.warning(
                    "Completa ambos campos."
                )

            else:

                try:

                    if iniciar_sesion(
                        correo.strip(),
                        password
                    ):

                        st.rerun()

                    else:

                        st.error(
                            "No se pudo iniciar sesión."
                        )

                except Exception:

                    st.error(
                        "Verifica tus credenciales "
                        "y la conexión."
                    )

        st.caption(
            "ElectraSafety Consultores | "
            "Acceso autorizado"
        )

        st.caption(
            f"NFPA 70E 2027 | Versión {VERSION}"
        )


if "usuario" not in st.session_state:

    mostrar_login()

    st.stop()


# RECUPERAR INFORMACIÓN

proyectos = []
clientes = {}
conexion_correcta = True

try:

    proyectos = consultar("proyectos")

    clientes = {
        c["id"]: c
        for c in consultar("clientes")
    }

except Exception:

    conexion_correcta = False

    logging.exception(
        "Error al recuperar información"
    )


opciones = {
    p["id"]: p for p in proyectos
}

activo = st.session_state.get(
    "proyecto_activo"
)

if conexion_correcta and activo not in opciones:

    activo = (
        proyectos[0]["id"]
        if proyectos else None
    )

    st.session_state["proyecto_activo"] = activo


# MENÚ LATERAL

with st.sidebar:

    if LOGO.exists():

        st.image(
            str(LOGO),
            use_container_width=True
        )

    st.markdown("### Electra Safe 360")

    st.caption(
        "Sistema de gestión de seguridad eléctrica"
    )

    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        list(MODULOS),
        key="pagina"
    )

    st.divider()

    st.markdown("### Proyecto activo")

    if activo in opciones:

        proyecto = opciones[activo]

        cliente = clientes.get(
            proyecto["cliente_id"],
            {}
        )

        st.write(
            cliente.get(
                "nombre_empresa",
                "Cliente"
            )
        )

        st.caption(
            proyecto.get("nombre", "")
        )

        st.caption(
            proyecto.get("codigo", "")
        )

    elif not conexion_correcta:

        st.caption(
            "Información temporalmente no disponible"
        )

    else:

        st.caption(
            "Sin proyecto seleccionado"
        )

    st.divider()

    st.caption("SESIÓN ACTIVA")

    st.write(
        st.session_state.usuario
    )

    if st.button(
        "Cerrar sesión",
        use_container_width=True
    ):

        try:

            cerrar_sesion()

            st.rerun()

        except Exception:

            st.error(
                "No se pudo cerrar la sesión."
            )

    st.caption(
        f"Versión {VERSION} | Proyecto académico"
    )


# TARJETAS DE NAVEGACIÓN

def tarjeta(nombre):

    datos = MODULOS[nombre]

    st.html(f"""
    <div class="modulo">
        <div class="modulo-titulo">
            {nombre}
        </div>
        <p>{datos["descripcion"]}</p>
    </div>
    """)

    st.button(
        "Acceder al módulo",
        key=f"abrir_{nombre}",
        on_click=navegar,
        args=(nombre,),
        use_container_width=True
    )


# PANTALLA PRINCIPAL

def mostrar_inicio():

    st.html("""
    <div class="banner">
        <div class="banner-titulo">
            Electra Safe 360
        </div>
        <div class="banner-subtitulo">
            Sistema integral para la evaluación,
            documentación y gestión de la
            seguridad eléctrica.
        </div>
        <div class="banner-norma">
            ELECTRASAFETY CONSULTORES
            &nbsp; | &nbsp;
            NFPA 70E 2027
        </div>
    </div>
    """)

    st.subheader("Resumen general")

    try:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Clientes",
            contar("clientes")
        )

        c2.metric(
            "Proyectos",
            contar("proyectos")
        )

        c3.metric(
            "Evaluaciones",
            contar("evaluaciones")
            + contar("arco_electrico")
        )

        c4.metric(
            "Documentos técnicos",
            contar("etiquetas")
            + contar("loto")
            + contar("permisos")
        )

        st.caption(
            "Conexión con la base de datos establecida."
        )

    except Exception:

        st.warning(
            "No se pudieron recuperar "
            "todos los indicadores."
        )

    st.subheader("Proyecto de trabajo")

    with st.container(border=True):

        if opciones:

            ids = list(opciones)

            actual = st.session_state.get(
                "proyecto_activo"
            )

            if actual not in ids:

                actual = ids[0]

            st.session_state[
                "selector_inicio"
            ] = actual

            def cambiar():

                st.session_state[
                    "proyecto_activo"
                ] = st.session_state[
                    "selector_inicio"
                ]

            seleccionado = st.selectbox(
                "Seleccionar proyecto activo",
                ids,
                format_func=lambda x: (
                    clientes.get(
                        opciones[x]["cliente_id"],
                        {}
                    ).get(
                        "nombre_empresa",
                        "Cliente"
                    )
                    + " | "
                    + opciones[x]["nombre"]
                ),
                key="selector_inicio",
                on_change=cambiar
            )

            p = opciones[seleccionado]

            st.caption(
                "Código: " + p["codigo"]
            )

            st.write(
                p.get("descripcion") or
                "Sin descripción registrada."
            )

        elif not conexion_correcta:

            st.warning(
                "No se pudieron consultar los proyectos."
            )

        else:

            st.info(
                "Registra un cliente y crea "
                "un proyecto para comenzar."
            )

    st.subheader("Administración")

    c1, c2 = st.columns(2)

    with c1:

        tarjeta("01. Clientes")

    with c2:

        tarjeta("02. Proyectos")

    st.subheader("Herramientas técnicas")

    herramientas = list(MODULOS)[3:]

    for i in range(0, len(herramientas), 3):

        columnas = st.columns(3)

        for columna, nombre in zip(
            columnas,
            herramientas[i:i+3]
        ):

            with columna:

                tarjeta(nombre)

    st.divider()

    with st.expander(
        "Acerca de Electra Safe 360"
    ):

        st.write(
            "Maletín digital desarrollado como "
            "herramienta de apoyo a la gestión "
            "de la seguridad eléctrica."
        )

        st.write(
            "Referencia normativa: NFPA 70E, "
            "edición 2027."
        )

        st.warning(
            "Aplicación académica. Los resultados "
            "requieren revisión por personal "
            "calificado antes de su utilización real."
        )

    with st.expander(
        "Equipo de desarrollo"
    ):

        for integrante in INTEGRANTES:

            st.write(integrante)

        st.caption(
            "ElectraSafety Consultores"
        )

    with st.expander(
        "Tecnologías utilizadas"
    ):

        st.write("Programación: Python")
        st.write("Interfaz: Streamlit")
        st.write("Base de datos: Supabase")
        st.write("Control de versiones: GitHub")
        st.write("Documentación PDF: ReportLab")
        st.write("Inteligencia artificial: ChatGPT")


# CARGAR MÓDULO SELECCIONADO

if pagina == "Inicio":

    mostrar_inicio()

else:

    st.caption(
        "Electra Safe 360 / " + pagina
    )

    st.button(
        "Volver al panel principal",
        on_click=navegar,
        args=("Inicio",),
        key="volver_inicio"
    )

    try:

        modulo = import_module(
            "modules."
            + MODULOS[pagina]["ruta"]
        )

        modulo.mostrar()

    except Exception:

        st.error(
            "No se pudo cargar este módulo."
        )

        st.caption(
            "Consulta los registros de Streamlit."
        )

        logging.exception(
            "Error al cargar %s",
            pagina
        )


# PIE DE PÁGINA

st.html(f"""
<div class="pie">
    <strong>ElectraSafety Consultores</strong>
    <br>
    Electra Safe 360 | Seguridad eléctrica
    | Versión {VERSION}
    <br>
    Herramienta académica
</div>
""")
