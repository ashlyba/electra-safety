
import streamlit as st

from pathlib import Path
from importlib import import_module
import logging

from database import (
    iniciar_sesion,
    cerrar_sesion,
    consultar,
    contar
)

from modules.estilos import aplicar_estilos


st.set_page_config(
    page_title="Electra Safe 360",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_estilos()

BASE_DIR = Path(__file__).resolve().parent
LOGO = BASE_DIR / "logo.png"

VERSION = "0.4"

INTEGRANTES = [
    "Pendiente de completar"
]


MODULOS = {
    "Inicio": {
        "icono": "🏠",
        "descripcion": "Panel de gestión"
    },
    "01. Clientes": {
        "icono": "🏢",
        "descripcion": (
            "Administración de empresas "
            "y contactos comerciales."
        ),
        "ruta": "clientes"
    },
    "02. Proyectos": {
        "icono": "📁",
        "descripcion": (
            "Organización y seguimiento "
            "de proyectos eléctricos."
        ),
        "ruta": "proyectos"
    },
    "03. Riesgos eléctricos": {
        "icono": "🛡️",
        "descripcion": (
            "Identificación de peligros, "
            "valoración y medidas de control."
        ),
        "ruta": "riesgos"
    },
    "04. Arco eléctrico y EPP": {
        "icono": "⚡",
        "descripcion": (
            "Evaluación de arco, choque "
            "eléctrico y protección personal."
        ),
        "ruta": "arco_electrico"
    },
    "05. Etiquetas": {
        "icono": "🏷️",
        "descripcion": (
            "Diseño, registro e impresión "
            "de etiquetas eléctricas."
        ),
        "ruta": "etiquetas"
    },
    "06. Bloqueo y etiquetado LOTO": {
        "icono": "🔒",
        "descripcion": (
            "Gestión documental del control "
            "de energías peligrosas."
        ),
        "ruta": "loto"
    },
    "07. Permisos de trabajo": {
        "icono": "📋",
        "descripcion": (
            "Gestión de permisos eléctricos "
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

        st.title("Bienvenido a Electra Safe 360")

        st.write(
            "Plataforma de gestión de "
            "seguridad eléctrica."
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
            "Acceso autorizado | "
            "ElectraSafety Consultores"
        )

        st.caption(
            "NFPA 70E 2027 | "
            f"Versión {VERSION}"
        )


if "usuario" not in st.session_state:

    mostrar_login()

    st.stop()


# RECUPERAR PROYECTO ACTIVO

proyectos = []
clientes = {}

try:

    proyectos = consultar("proyectos")

    clientes = {
        c["id"]: c
        for c in consultar("clientes")
    }

except Exception:

    logging.exception(
        "No se pudieron consultar proyectos"
    )


opciones = {
    p["id"]: p for p in proyectos
}

activo = st.session_state.get(
    "proyecto_activo"
)

if activo not in opciones:

    activo = (
        proyectos[0]["id"]
        if proyectos else None
    )

    st.session_state[
        "proyecto_activo"
    ] = activo


# MENU LATERAL

with st.sidebar:

    if LOGO.exists():

        st.image(
            str(LOGO),
            use_container_width=True
        )

    st.markdown("### Electra Safe 360")

    st.caption(
        "SISTEMA DE GESTIÓN ELÉCTRICA"
    )

    st.divider()

    pagina = st.radio(
        "ESPACIO DE TRABAJO",
        list(MODULOS),
        format_func=lambda x: (
            MODULOS[x]["icono"]
            + "  "
            + x
        ),
        key="pagina"
    )

    st.divider()

    st.markdown("### Proyecto activo")

    if activo in opciones:

        proyecto = opciones[activo]

        cliente = clientes.get(
            proyecto["cliente_id"], {}
        )

        st.write(
            cliente.get(
                "nombre_empresa",
                "Cliente"
            )
        )

        st.caption(proyecto["nombre"])

    else:

        st.caption(
            "Sin proyecto seleccionado"
        )

    st.divider()

    st.caption("SESIÓN ACTIVA")

    st.write(st.session_state.usuario)

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
        f"Versión {VERSION} | "
        "Proyecto académico"
    )


# FUNCIONES DE INICIO

def tarjeta(nombre):

    datos = MODULOS[nombre]

    st.html(f"""
    <div class="modulo">
        <div style="font-size:28px;
                    margin-bottom:12px;">
            {datos["icono"]}
        </div>
        <div class="modulo-titulo">
            {nombre}
        </div>
        <p>{datos["descripcion"]}</p>
    </div>
    """)

    st.button(
        "Acceder al módulo →",
        key=f"abrir_{nombre}",
        on_click=navegar,
        args=(nombre,),
        use_container_width=True
    )


def mostrar_inicio():

    st.html("""
    <div class="banner">
        <div class="banner-titulo">
            Electra Safe 360
        </div>
        <div class="banner-subtitulo">
            Plataforma integral para la evaluación,
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

    st.subheader("Panel de gestión")

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
            "● Conexión con la base de datos establecida."
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
                        "nombre_empresa", "Cliente"
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

    c1, c2 = st.columns(2)

    with c1:

        with st.expander(
            "Acerca de Electra Safe 360"
        ):

            st.write(
                "Maletín digital de apoyo "
                "a la gestión de la seguridad "
                "eléctrica."
            )

            st.write(
                "Referencia: NFPA 70E, "
                "edición 2027."
            )

            st.warning(
                "Aplicación académica. "
                "No sustituye la evaluación "
                "de personal calificado."
            )

    with c2:

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

        st.write(
            "Python · Streamlit · Supabase "
            "· GitHub · ReportLab"
        )

        st.write(
            "Inteligencia artificial: ChatGPT"
        )


# CARGAR PANTALLA

if pagina == "Inicio":

    mostrar_inicio()

else:

    st.caption(
        "Electra Safe 360 / " + pagina
    )

    st.button(
        "← Volver al panel principal",
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
            "Consulta los registros de "
            "Streamlit para identificar el error."
        )

        logging.exception(
            "Error al cargar %s",
            pagina
        )


st.html(f"""
<div class="pie">
    <strong>ElectraSafety Consultores</strong>
    <br>
    Electra Safe 360 · Seguridad eléctrica
    · Versión {VERSION}
    <br>
    Herramienta académica
</div>
""")
