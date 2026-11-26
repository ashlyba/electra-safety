
from io import BytesIO
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from database import consultar


AZUL = colors.HexColor("#0C2335")
AMARILLO = colors.HexColor("#FFB900")
GRIS = colors.HexColor("#F1F5F9")

LOGO = Path(__file__).resolve().parent.parent / "logo.png"


def texto_seguro(valor):

    if valor is None or valor == "":
        return "No registrado"

    if isinstance(valor, list):
        valor = "; ".join(str(v) for v in valor)

    return escape(str(valor)).replace("\n", "<br/>")


def pie_pagina(canvas, doc):

    ancho, alto = letter

    canvas.setStrokeColor(AMARILLO)
    canvas.line(40, 48, ancho - 40, 48)

    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        40, 33,
        "ElectraSafety Consultores | Electra Safe 360"
    )

    canvas.drawRightString(
        ancho - 40, 33,
        f"Página {doc.page}"
    )


def generar_pdf(
    titulo,
    proyecto,
    secciones,
    referencia=""
):

    memoria = BytesIO()

    doc = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=65
    )

    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="TituloElectra",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=23,
        textColor=AZUL,
        alignment=TA_CENTER,
        spaceAfter=15
    ))

    estilos.add(ParagraphStyle(
        name="SeccionElectra",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=AZUL,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    ))

    estilos.add(ParagraphStyle(
        name="CeldaElectra",
        fontName="Helvetica",
        fontSize=9,
        leading=13
    ))

    elementos = []

    if LOGO.exists():

        imagen = Image(str(LOGO))

        proporcion = imagen.imageHeight / imagen.imageWidth

        imagen.drawWidth = 230
        imagen.drawHeight = 230 * proporcion

        elementos.append(imagen)
        elementos.append(Spacer(1, 15))

    elementos.append(
        Paragraph(
            texto_seguro(titulo),
            estilos["TituloElectra"]
        )
    )

    clientes = consultar(
        "clientes",
        {"id": proyecto["cliente_id"]}
    )

    cliente = clientes[0] if clientes else {}

    informacion = {
        "Cliente": cliente.get("nombre_empresa"),
        "Proyecto": proyecto.get("nombre"),
        "Código": proyecto.get("codigo"),
        "Fecha de emisión": datetime.now().strftime(
            "%d/%m/%Y"
        )
    }

    def agregar_tabla(campos):

        filas = []

        for nombre, valor in campos.items():

            filas.append([
                Paragraph(
                    "<b>" + texto_seguro(nombre) + "</b>",
                    estilos["CeldaElectra"]
                ),
                Paragraph(
                    texto_seguro(valor),
                    estilos["CeldaElectra"]
                )
            ])

        if not filas:
            return

        tabla = Table(
            filas,
            colWidths=[145, 375],
            hAlign="LEFT",
            splitByRow=1,
            splitInRow=1
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), GRIS),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.35,
             colors.HexColor("#CBD5E1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 10))

    agregar_tabla(informacion)

    for nombre, campos in secciones:

        elementos.append(
            Paragraph(
                texto_seguro(nombre),
                estilos["SeccionElectra"]
            )
        )

        agregar_tabla(campos)

    if referencia:

        elementos.append(
            Paragraph(
                "Referencia técnica",
                estilos["SeccionElectra"]
            )
        )

        elementos.append(
            Paragraph(
                texto_seguro(referencia),
                estilos["Normal"]
            )
        )

    elementos.append(Spacer(1, 15))

    elementos.append(
        Paragraph(
            "Documento académico de apoyo. "
            "No constituye una autorización de trabajo "
            "ni sustituye la revisión de una persona calificada.",
            estilos["Normal"]
        )
    )

    doc.build(
        elementos,
        onFirstPage=pie_pagina,
        onLaterPages=pie_pagina
    )

    memoria.seek(0)

    return memoria.getvalue()
