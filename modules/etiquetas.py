
import streamlit as st
import pandas as pd

from io import BytesIO
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph,
    Table, TableStyle, Spacer, KeepTogether
)

from database import consultar, insertar
from modules.comunes import (
    seleccionar_proyecto,
    mostrar_aviso,
    notificar,
    advertencia_tecnica
)


def generar_etiquetas(etiquetas):

    memoria = BytesIO()

    doc = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    normal = ParagraphStyle(
        "NormalEtiqueta",
        fontSize=11,
        leading=15
    )

    encabezado = ParagraphStyle(
        "EncabezadoEtiqueta",
        fontSize=20,
        leading=24,
        alignment=1,
        fontName="Helvetica-Bold"
    )

    elementos = []

    for detalle in etiquetas:

        filas = [
            [
                Paragraph(
                    "ADVERTENCIA",
                    encabezado
                )
            ],
            [
                Paragraph(
                    "<b>PELIGRO DE ARCO Y CHOQUE ELECTRICO</b>",
                    normal
                )
            ],
            [
                Paragraph(
                    "MUESTRA ACADEMICA - NO UTILIZAR EN CAMPO",
                    normal
                )
            ]
        ]

        for campo, valor in detalle.items():

            filas.append([
                Paragraph(
                    f"<b>{escape(str(campo))}:</b> "
                    f"{escape(str(valor))}",
                    normal
                )
            ])

        filas.append([
            Paragraph(
                "<b>ElectraSafety Consultores</b>",
                normal
            )
        ])

        tabla = Table(
            filas,
            colWidths=[500]
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0),
             colors.HexColor("#E97719")),
            ("BOX", (0, 0), (-1, -1),
             1.5, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 12)
        ]))

        elementos.append(
            KeepTogether([tabla, Spacer(1, 18)])
        )

    doc.build(elementos)

    return memoria.getvalue()


def preparar_etiqueta(detalle, referencia, revision):

    return {
        "Equipo": detalle.get("Equipo"),
        "Ubicación": detalle.get("Ubicación"),
        "Tensión nominal": (
            f"{detalle.get('Tensión (V)')} "
            f"V {detalle.get('Sistema')}"
        ),
        "Frontera de arco": (
            f"{detalle.get('Frontera de arco')} m"
        ),
        "Categoría de EPP": detalle.get("Categoría"),
        "Identificación de evaluación": referencia,
        "Revisión": revision,
        "Referencia": detalle.get("Referencia arco"),
        "Estado": "Muestra académica"
    }


def vista_previa(detalle):

    with st.container(border=True):

        st.markdown(
            """
            <div style="background:#E97719;
            color:black;text-align:center;
            padding:12px;font-size:25px;
            font-weight:bold;">
            ADVERTENCIA
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "### PELIGRO DE ARCO Y CHOQUE ELÉCTRICO"
        )

        st.error(
            "MUESTRA ACADÉMICA — NO UTILIZAR EN CAMPO"
        )

        for campo, valor in detalle.items():
            st.write(f"**{campo}:** {valor}")

        st.caption("ElectraSafety Consultores")


def mostrar():

    st.title("05. Diseño e impresión de etiquetas")

    advertencia_tecnica()
    mostrar_aviso("etiquetas")

    proyecto = seleccionar_proyecto("etiquetas")

    if not proyecto:
        return

    tab1, tab2 = st.tabs([
        "Crear etiquetas",
        "Etiquetas guardadas"
    ])

    with tab1:

        registros = consultar(
            "arco_electrico",
            {"proyecto_id": proyecto["id"]}
        )

        registros = [
            r for r in registros
            if (r.get("detalle") or {}).get(
                "Método aplicable"
            ) == "Sí"
        ]

        buscar = st.text_input(
            "Buscar equipo o ubicación"
        )

        categoria = st.selectbox(
            "Categoría de EPP",
            ["Todas", 1, 2, 3, 4]
        )

        opciones = {}

        for r in registros:

            d = r.get("detalle") or {}

            texto = (
                str(d.get("Equipo", ""))
                + " "
                + str(d.get("Ubicación", ""))
            )

            if buscar.lower() not in texto.lower():
                continue

            if (
                categoria != "Todas"
                and d.get("Categoría") != categoria
            ):
                continue

            opciones[r["id"]] = r

        seleccion = st.multiselect(
            "Seleccionar uno o varios equipos",
            list(opciones),
            format_func=lambda x: (
                opciones[x]["detalle"].get("Equipo", "")
                + " | " + str(x)[:8]
            )
        )

        revision = st.text_input(
            "Identificación de revisión",
            value="Rev. 01"
        )

        etiquetas = [
            preparar_etiqueta(
                opciones[x]["detalle"],
                x,
                revision
            )
            for x in seleccion
        ]

        if etiquetas:

            st.subheader("Vista previa")

            for etiqueta in etiquetas:
                vista_previa(etiqueta)

            st.download_button(
                "Descargar lote de etiquetas",
                generar_etiquetas(etiquetas),
                "etiquetas_electricas.pdf",
                "application/pdf"
            )

            if st.button(
                "Guardar etiquetas",
                type="primary"
            ):

                try:

                    existentes = consultar(
                        "etiquetas",
                        {"proyecto_id": proyecto["id"]}
                    )

                    guardadas = [
                        r.get("detalle")
                        for r in existentes
                    ]

                    cantidad = 0

                    for etiqueta in etiquetas:

                        if etiqueta not in guardadas:

                            respuesta = insertar(
                                "etiquetas",
                                {
                                    "proyecto_id": proyecto["id"],
                                    "detalle": etiqueta
                                }
                            )

                            if respuesta:
                                cantidad += 1

                    if cantidad:

                        notificar(
                            "etiquetas",
                            f"{cantidad} etiquetas guardadas."
                        )

                    else:
                        st.warning(
                            "Las etiquetas ya estaban registradas."
                        )

                except Exception as error:
                    st.error(str(error))

        else:

            st.info(
                "Selecciona evaluaciones del módulo 4 "
                "para generar etiquetas."
            )

    with tab2:

        registros = consultar(
            "etiquetas",
            {"proyecto_id": proyecto["id"]}
        )

        if not registros:

            st.info("No hay etiquetas guardadas.")
            return

        detalles = [
            r.get("detalle") or {}
            for r in registros
        ]

        st.dataframe(
            pd.DataFrame(detalles),
            hide_index=True,
            use_container_width=True
        )

        opciones = {
            r["id"]: r for r in registros
        }

        seleccion = st.multiselect(
            "Etiquetas para imprimir",
            list(opciones),
            format_func=lambda x: (
                opciones[x]["detalle"].get("Equipo", "")
                + " | " + str(x)[:8]
            )
        )

        if seleccion:

            st.download_button(
                "Imprimir etiquetas seleccionadas",
                generar_etiquetas([
                    opciones[x]["detalle"]
                    for x in seleccion
                ]),
                "etiquetas_guardadas.pdf",
                "application/pdf"
            )
