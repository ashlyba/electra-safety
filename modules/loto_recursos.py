from modules.reportes import cache_pdf, encabezado_pagina

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import (
    Drawing, Rect, Circle, Line, String, Path
)
from reportlab.graphics import renderSVG
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, KeepTogether
)

AZUL = colors.HexColor("#0C2335")
AMARILLO = colors.HexColor("#FFB900")
ROJO = colors.HexColor("#B91C1C")
GRIS = colors.HexColor("#CBD5E1")


def ilustracion(tipo):
    d = Drawing(220, 140)

    d.add(Rect(
        0, 0, 220, 140,
        fillColor=colors.HexColor("#F1F5F9"),
        strokeColor=None
    ))

    if tipo == "candado":
        d.add(Rect(
            78, 70, 64, 55,
            rx=28, ry=28,
            fillColor=None,
            strokeColor=AZUL,
            strokeWidth=9
        ))

        d.add(Rect(
            65, 25, 90, 65,
            rx=8, ry=8,
            fillColor=ROJO,
            strokeColor=AZUL
        ))

        d.add(Circle(
            110, 50, 6,
            fillColor=AZUL
        ))

    elif tipo == "pinza":
        d.add(Circle(
            110, 105, 25,
            fillColor=None,
            strokeColor=AZUL,
            strokeWidth=8
        ))

        d.add(Rect(
            85, 15, 50, 75,
            rx=10, ry=10,
            fillColor=ROJO,
            strokeColor=AZUL
        ))

        for y in [30, 48, 66]:
            for x in [98, 122]:
                d.add(Circle(
                    x, y, 5,
                    fillColor=colors.white
                ))

    elif tipo == "interruptor":
        d.add(Rect(
            60, 20, 100, 100,
            fillColor=GRIS,
            strokeColor=AZUL
        ))

        d.add(Rect(
            85, 50, 50, 45,
            fillColor=ROJO,
            strokeColor=AZUL
        ))

        d.add(Circle(
            110, 75, 8,
            fillColor=colors.white
        ))

    elif tipo == "enchufe":
        d.add(Rect(
            45, 35, 130, 70,
            rx=20, ry=20,
            fillColor=ROJO,
            strokeColor=AZUL
        ))

        d.add(Line(
            0, 70, 45, 70,
            strokeColor=AZUL,
            strokeWidth=8
        ))

        d.add(Circle(
            155, 70, 7,
            fillColor=colors.white
        ))

    elif tipo == "valvula":
        d.add(Circle(
            110, 70, 50,
            fillColor=ROJO,
            strokeColor=AZUL,
            strokeWidth=3
        ))

        d.add(Circle(
            110, 70, 20,
            fillColor=GRIS,
            strokeColor=AZUL
        ))

        d.add(Circle(
            150, 70, 7,
            fillColor=colors.white
        ))

    elif tipo == "seccionador":
        d.add(Rect(46, 18, 128, 104, fillColor=GRIS, strokeColor=AZUL))
        d.add(Line(61, 57, 101, 57, strokeColor=AZUL, strokeWidth=4))
        d.add(Line(101, 57, 141, 87, strokeColor=AZUL, strokeWidth=4))
        d.add(Line(144, 57, 159, 57, strokeColor=AZUL, strokeWidth=4))
        d.add(Circle(100, 57, 5, fillColor=AZUL))
        d.add(Circle(144, 57, 5, fillColor=AZUL))
        d.add(Rect(81, 33, 31, 22, fillColor=ROJO, strokeColor=AZUL))
        d.add(String(110, 7, "Seccionador abierto", textAnchor="middle", fontSize=10))

    elif tipo == "caja":
        d.add(Rect(
            75, 105, 70, 22,
            rx=8, ry=8,
            fillColor=None,
            strokeColor=AZUL,
            strokeWidth=5
        ))

        d.add(Rect(
            40, 20, 140, 90,
            rx=5, ry=5,
            fillColor=ROJO,
            strokeColor=AZUL
        ))

        for x in [60, 85, 110, 135, 160]:
            d.add(Circle(
                x, 35, 5,
                fillColor=colors.white
            ))

        d.add(String(
            110, 75,
            "LOTO",
            textAnchor="middle",
            fontName="Helvetica-Bold",
            fontSize=20,
            fillColor=colors.white
        ))

    return d


def imagen_svg(tipo):
    return renderSVG.drawToString(
        ilustracion(tipo)
    )


@cache_pdf
def generar_catalogo_pdf(dispositivos, referencia=""):
    memoria = BytesIO()

    doc = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=105,
        bottomMargin=65
    )

    estilos = getSampleStyleSheet()

    elementos = [
        Paragraph(
            "ElectraSafety Consultores",
            estilos["Title"]
        ),
        Paragraph(
            "Catálogo de dispositivos LOTO",
            estilos["Heading1"]
        ),
        Paragraph(
            "Ilustraciones esquemáticas de referencia. "
            "La selección definitiva requiere verificar "
            "las especificaciones del fabricante.",
            estilos["Normal"]
        ),
        Spacer(1, 15)
    ]

    for dispositivo in dispositivos:
        bloque = [
            Paragraph(
                escape(dispositivo["Nombre"]),
                estilos["Heading2"]
            ),
            ilustracion(dispositivo["ID"]),
            Spacer(1, 8)
        ]

        for campo, valor in dispositivo.items():
            if campo not in ["ID", "Nombre"]:
                bloque.append(
                    Paragraph(
                        f"<b>{escape(campo)}:</b> "
                        f"{escape(str(valor))}",
                        estilos["Normal"]
                    )
                )

                bloque.append(Spacer(1, 5))

        elementos.append(KeepTogether(bloque))
        elementos.append(Spacer(1, 20))

    if referencia:
        elementos.append(Paragraph(escape(referencia), estilos["Normal"]))

    doc.build(elementos, onFirstPage=encabezado_pagina, onLaterPages=encabezado_pagina)

    return memoria.getvalue()


@cache_pdf
def generar_loto_pdf(etiquetas):
    memoria = BytesIO()

    doc = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    estilos = getSampleStyleSheet()
    elementos = []

    for detalle in etiquetas:
        filas = [
            [
                Paragraph(
                    '<font color="white" size="18">'
                    '<b>PELIGRO - NO OPERAR</b></font>',
                    estilos["Normal"]
                )
            ],
            [
                Paragraph(
                    "<b>CONTROL DE ENERGÍAS PELIGROSAS</b>",
                    estilos["Normal"]
                )
            ]
        ]

        for campo, valor in detalle.items():
            filas.append([
                Paragraph(
                    f"<b>{escape(str(campo))}:</b> "
                    f"{escape(str(valor))}",
                    estilos["Normal"]
                )
            ])

        filas.append([
            Paragraph(
                "<b>No retirar sin autorización.</b>",
                estilos["Normal"]
            )
        ])

        filas.append([
            Paragraph(
                "ElectraSafety Consultores",
                estilos["Normal"]
            )
        ])

        filas.append([
            Paragraph(
                "MUESTRA ACADÉMICA - NO UTILIZAR EN CAMPO",
                estilos["Normal"]
            )
        ])

        tabla = Table(
            filas,
            colWidths=[260],
            hAlign="CENTER",
            splitInRow=1
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), ROJO),
            ("BOX", (0, 0), (-1, -1), 2, ROJO),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12)
        ]))

        elementos.append(
            KeepTogether([
                tabla,
                Spacer(1, 20)
            ])
        )

    doc.build(elementos)

    return memoria.getvalue()
