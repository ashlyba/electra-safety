
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
from modules.comunes import mostrar_avance


BASE_DIR = Path(__file__).resolve().parent
LOGO = BASE_DIR / "logo.png"

VERSION = "1.0"

INTEGRANTES = [
    "Ashly Barrantes"
    "Nicole Valverde"
    "Xochilt Velasquez"
    "Cristian Fonseca"
]


st.set_page_config(
    page_title="Electra Safe 360",
    page_icon=str(LOGO) if LOGO.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_estilos()


MODULOS = {
    "Inicio": (
        None,
        "Panel general de gestión"
    ),
    "01. Clientes": (
        "clientes",
        "Administración de empresas y contactos."
    ),
    "02. Proyectos": (
        "proyectos",
        "Organización y seguimiento de proyectos."
    ),
    "03. Riesgos eléctricos": (
        "riesgos",
        "Identificación y valoración de riesgos."
    ),
    "04. Arco eléctrico y EPP": (
        "arco_electrico",
        "Evaluación de arco, choque y protección."
    ),
    "05. Etiquetas": (
        "etiquetas",
        "Diseño e impresión de etiquetas eléctricas."
    ),
    "06. Bloqueo y etiquetado LOTO": (
        "loto",
        "Control de energías peligrosas."
    ),
    "07. Permisos de trabajo": (
        "permisos",
        "Documentación de trabajos eléctricos."
    ),
    "Manual de uso": (
        "ayuda",
        "Orientación para utilizar el sistema."
    )
}


def navegar(destino):

    actual = st.session_state.get(
        "pagina_actual",
        "Inicio"
    )

    if destino == actual:

        return

    if actual in (
        "Inicio",
        "Manual de uso"
    ):

        st.session_state[
            "pagina_actual"
        ] = destino

    else:

        st.session_state[
            "destino_pendiente"
        ] = destino


def confirmar_navegacion():

    destino = st.session_state.pop(
        "destino_pendiente",
        None
    )

    if destino:

        st.session_state[
            "pagina_actual"
        ] = destino


def cancelar_navegacion():

    st.session_state.pop(
        "destino_pendiente",
        None
    )


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
            "Sistema integral de gestión "
            "de seguridad eléctrica"
        )

        with st.form("login"):

            st.subheader("Acceso al sistema")

            correo = st.text_input(
                "Correo electrónico"
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
                    "Complete ambos campos."
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
                        "Verifique las credenciales "
                        "y la conexión."
                    )

        st.caption(
            "ElectraSafety Consultores"
            f" | Versión {VERSION}"
        )


if not st.session_state.get("usuario"):

    mostrar_login()
    st.stop()


st.session_state.setdefault(
    "pagina_actual",
    "Inicio"
)

pagina = st.session_state[
    "pagina_actual"
]

if pagina not in MODULOS:

    pagina = "Inicio"

    st.session_state[
        "pagina_actual"
    ] = pagina


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
        "Error de consulta general"
    )


opciones = {
    p["id"]: p
    for p in proyectos
}

activo = st.session_state.get(
    "proyecto_activo"
)

if conexion_correcta and activo not in opciones:

    activo = (
        next(iter(opciones))
        if opciones
        else None
    )

    st.session_state[
        "proyecto_activo"
    ] = activo


with st.sidebar:

    if LOGO.exists():

        st.image(
            str(LOGO),
            use_container_width=True
        )

    st.markdown("### Electra Safe 360")

    st.caption(
        "ElectraSafety Consultores"
    )

    st.divider()

    grupos = {
        "GENERAL": [
            "Inicio"
        ],
        "ADMINISTRACIÓN": [
            "01. Clientes",
            "02. Proyectos"
        ],
        "GESTIÓN TÉCNICA": [
            "03. Riesgos eléctricos",
            "04. Arco eléctrico y EPP",
            "05. Etiquetas",
            "06. Bloqueo y etiquetado LOTO",
            "07. Permisos de trabajo"
        ],
        "DOCUMENTACIÓN": [
            "Manual de uso"
        ]
    }

    for grupo, nombres in grupos.items():

        st.caption(grupo)

        for nombre in nombres:

            st.button(
                nombre,
                key=f"nav_{nombre}",
                type=(
                    "primary"
                    if pagina == nombre
                    else "secondary"
                ),
                use_container_width=True,
                on_click=navegar,
                args=(nombre,)
            )

    st.divider()

    st.markdown("### Proyecto activo")

    if activo in opciones:

        proyecto = opciones[activo]

        cliente = clientes.get(
            proyecto.get("cliente_id"),
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

        mostrar_avance(
            activo,
            compacto=True
        )

    else:

        st.caption(
            "Sin proyecto disponible."
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

        st.session_state[
            "confirmar_salida"
        ] = True

    st.caption(
        f"Versión {VERSION}"
    )


if st.session_state.get(
    "confirmar_salida"
):

    with st.container(border=True):

        st.warning(
            "Guarde los cambios antes de cerrar sesión."
        )

        c1, c2 = st.columns(2)

        if c1.button(
            "Confirmar cierre",
            type="primary"
        ):

            cerrar_sesion()
            st.rerun()

        if c2.button("Cancelar"):

            st.session_state.pop(
                "confirmar_salida",
                None
            )

            st.rerun()


if st.session_state.get(
    "destino_pendiente"
):

    with st.container(border=True):

        st.warning(
            "Los cambios sin guardar podrían perderse "
            "al abandonar este módulo."
        )

        st.write(
            "Destino: "
            + st.session_state["destino_pendiente"]
        )

        c1, c2 = st.columns(2)

        c1.button(
            "Continuar",
            type="primary",
            on_click=confirmar_navegacion,
            use_container_width=True
        )

        c2.button(
            "Permanecer en el módulo",
            on_click=cancelar_navegacion,
            use_container_width=True
        )


def tarjeta(nombre):

    ruta, descripcion = MODULOS[nombre]

    st.html(f"""
    <div class="modulo">
        <div class="modulo-titulo">
            {nombre}
        </div>
        <p>{descripcion}</p>
    </div>
    """)

    st.button(
        "Acceder al módulo",
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
            Sistema integral para la evaluación,
            documentación y gestión de la
            seguridad eléctrica.
        </div>
        <div class="banner-norma">
            ELECTRASAFETY CONSULTORES
            &nbsp; | &nbsp; NFPA 70E 2027
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

    except Exception:

        st.warning(
            "Indicadores temporalmente no disponibles."
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
                "Seleccionar proyecto existente",
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

            proyecto = opciones[seleccionado]

            st.write(
                "**Código:**",
                proyecto.get("codigo")
            )

            st.write(
                proyecto.get("descripcion")
                or "Sin descripción registrada."
            )

            mostrar_avance(seleccionado)

        else:

            st.info(
                "Registre un cliente y un proyecto "
                "para comenzar."
            )

        st.button(
            "Administrar o crear proyectos",
            on_click=navegar,
            args=("02. Proyectos",)
        )

    st.subheader("Administración")

    c1, c2 = st.columns(2)

    with c1:

        tarjeta("01. Clientes")

    with c2:

        tarjeta("02. Proyectos")

    st.subheader("Herramientas técnicas")

    herramientas = list(MODULOS)[3:8]

    for i in range(
        0,
        len(herramientas),
        3
    ):

        columnas = st.columns(3)

        for columna, nombre in zip(
            columnas,
            herramientas[i:i+3]
        ):

            with columna:

                tarjeta(nombre)

    st.divider()

    with st.expander(
        "Acerca del sistema"
    ):

        st.write(
            "Maletín digital académico de apoyo "
            "a la gestión de seguridad eléctrica."
        )

        st.write(
            "Referencia normativa: NFPA 70E, "
            "edición 2027."
        )

        st.write(
            "Inteligencia artificial utilizada: ChatGPT."
        )

        st.caption(
            "Los resultados requieren revisión "
            "por personal calificado."
        )

    with st.expander(
        "Equipo de desarrollo"
    ):

        for integrante in INTEGRANTES:

            st.write(integrante)

    st.button(
        "Consultar manual de uso",
        on_click=navegar,
        args=("Manual de uso",)
    )


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

        ruta = MODULOS[pagina][0]

        modulo = import_module(
            "modules." + ruta
        )

        modulo.mostrar()

    except Exception:

        st.error(
            "No se pudo cargar el módulo."
        )

        logging.exception(
            "Error al cargar %s",
            pagina
        )


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
