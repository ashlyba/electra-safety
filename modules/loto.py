
import streamlit as st

from modules.comunes import (
    seleccionar_proyecto,
    advertencia_tecnica
)

from modules.documentos import administrar_documentos
from modules.etiquetas import generar_etiquetas


CATALOGO = [
    {
        "Nombre": "Candado de seguridad",
        "Función": "Impedir la operación no autorizada.",
        "Aplicación": "Dispositivos y puntos de aislamiento.",
        "Compatibilidad": "Verificar diámetro del arco y dispositivo.",
        "Colocación": "Según instrucciones del fabricante.",
        "Limitación": "No sustituye el aislamiento ni su verificación."
    },
    {
        "Nombre": "Pinza de bloqueo múltiple",
        "Función": "Permitir varios candados en un punto.",
        "Aplicación": "Bloqueos con varios participantes.",
        "Compatibilidad": "Verificar dimensiones y capacidad.",
        "Colocación": "Según el procedimiento de bloqueo grupal.",
        "Limitación": "No exceder la capacidad del dispositivo."
    },
    {
        "Nombre": "Bloqueador de interruptores",
        "Función": "Restringir el accionamiento del interruptor.",
        "Aplicación": "Interruptores automáticos compatibles.",
        "Compatibilidad": "Verificar marca, modelo y dimensiones.",
        "Colocación": "Conforme al manual específico.",
        "Limitación": "No todos los modelos son universales."
    },
    {
        "Nombre": "Bloqueador de enchufes",
        "Función": "Impedir la reconexión de un enchufe.",
        "Aplicación": "Equipos alimentados mediante enchufe.",
        "Compatibilidad": "Verificar tamaño y configuración.",
        "Colocación": "Según instrucciones del fabricante.",
        "Limitación": "Considerar otras fuentes de energía."
    },
    {
        "Nombre": "Bloqueador de válvulas",
        "Función": "Restringir la operación de una válvula.",
        "Aplicación": "Fuentes de energía hidráulica o neumática.",
        "Compatibilidad": "Verificar tipo y diámetro de válvula.",
        "Colocación": "Según el dispositivo seleccionado.",
        "Limitación": "No elimina la presión residual."
    },
    {
        "Nombre": "Caja de bloqueo grupal",
        "Función": "Gestionar las llaves de aislamiento.",
        "Aplicación": "Procedimientos con múltiples participantes.",
        "Compatibilidad": "Verificar capacidad y sistema de cierre.",
        "Colocación": "Según el procedimiento grupal aprobado.",
        "Limitación": "Requiere control de participantes y llaves."
    }
]


POLITICA = {
    "Información general": [
        "Identificación",
        "Objetivo",
        "Alcance",
        "Equipos incluidos"
    ],
    "Responsabilidades": [
        "Responsable del programa",
        "Personal autorizado",
        "Personal afectado",
        "Capacitación y auditoría"
    ],
    "Planificación y control": [
        "Identificación de fuentes de energía",
        "Notificación al personal",
        "Parada del equipo",
        "Puntos y medios de aislamiento",
        "Dispositivos de bloqueo y etiquetado",
        "Control de energía almacenada",
        "Verificación de aislamiento y ausencia de tensión"
    ],
    "Situaciones especiales": [
        "Bloqueo grupal",
        "Cambio de turno",
        "Retiro excepcional de dispositivos",
        "Contratistas"
    ],
    "Restitución del servicio": [
        "Inspección previa",
        "Retiro controlado de dispositivos",
        "Notificación y restitución",
        "Responsable de revisión"
    ]
}


def mostrar():

    st.title("06. Bloqueo y etiquetado LOTO")

    advertencia_tecnica()

    proyecto = seleccionar_proyecto("loto")

    if not proyecto:
        return

    tab1, tab2, tab3 = st.tabs([
        "Catálogo de dispositivos",
        "Política y procedimiento",
        "Etiquetas LOTO"
    ])

    with tab1:

        st.subheader("Catálogo técnico")

        seleccion = st.multiselect(
            "Seleccionar dispositivos",
            [d["Nombre"] for d in CATALOGO]
        )

        for dispositivo in CATALOGO:

            if dispositivo["Nombre"] not in seleccion:
                continue

            with st.container(border=True):

                st.subheader(dispositivo["Nombre"])

                for campo, valor in dispositivo.items():

                    if campo != "Nombre":
                        st.write(f"**{campo}:** {valor}")

                referencia = st.text_input(
                    "Fabricante, modelo y referencia técnica",
                    key="ref_" + dispositivo["Nombre"]
                )

                imagen = st.file_uploader(
                    "Agregar fotografía del dispositivo",
                    type=["png", "jpg", "jpeg"],
                    key="img_" + dispositivo["Nombre"]
                )

                if imagen:
                    st.image(imagen, width=250)

                if not referencia:
                    st.caption(
                        "Pendiente de referencia del fabricante."
                    )

        st.info(
            "Las fotografías y referencias del fabricante "
            "deben corresponder al dispositivo real."
        )

    with tab2:

        administrar_documentos(
            "loto",
            proyecto,
            "Política y procedimiento LOTO",
            POLITICA,
            "NFPA 70E 2027, artículo 120.",
            tipo="Política LOTO"
        )

    with tab3:

        st.subheader("Diseño de etiqueta LOTO")

        nombre = st.text_input("Nombre del responsable")
        equipo = st.text_input("Equipo bloqueado")
        motivo = st.text_area("Motivo del bloqueo")
        contacto = st.text_input("Teléfono o contacto")
        fecha = st.date_input("Fecha de colocación")
        codigo = st.text_input("Código de candado o etiqueta")

        cantidad = st.number_input(
            "Cantidad de etiquetas",
            min_value=1,
            max_value=30,
            value=1
        )

        with st.container(border=True):

            st.markdown(
                """
                <div style="background:#B91C1C;
                color:white;padding:15px;
                text-align:center;font-size:28px;
                font-weight:bold;">
                PELIGRO
                </div>
                """,
                unsafe_allow_html=True
            )

            st.title("NO OPERAR")

            st.write(f"**Responsable:** {nombre}")
            st.write(f"**Equipo:** {equipo}")
            st.write(f"**Motivo:** {motivo}")
            st.write(f"**Contacto:** {contacto}")
            st.write(f"**Fecha:** {fecha}")
            st.write(f"**Código:** {codigo}")

            st.warning(
                "Prohibido operar o retirar esta etiqueta "
                "sin autorización."
            )

        st.caption(
            "Vista previa académica. La etiqueta física "
            "debe cumplir los requisitos de material y fijación."
        )

        if not all([nombre, equipo, motivo, codigo]):
            st.info("Completa los campos para continuar.")
