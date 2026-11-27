from collections import OrderedDict
from functools import wraps
from hashlib import sha256
from io import BytesIO
import json

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from database import consultar


AZUL = colors.HexColor("#0C2335")
AMARILLO = colors.HexColor("#FFB900")
GRIS = colors.HexColor("#F1F5F9")
BORDE = colors.HexColor("#CBD5E1")

LOGO = (
    Path(__file__).resolve().parent.parent
    / "logo.png"
)


def cache_pdf(funcion):
    """Conserva PDFs recientes de la sesión, con un límite de memoria."""
    @wraps(funcion)
    def obtener(*args, **kwargs):
        if get_script_run_ctx(suppress_warning=True) is None:
            return funcion(*args, **kwargs)
        contenido = json.dumps([args, kwargs], ensure_ascii=False, default=str)
        clave = (funcion.__module__, funcion.__name__, sha256(contenido.encode()).digest())
        cache = st.session_state.setdefault("_pdf_cache", OrderedDict())
        if clave in cache:
            cache.move_to_end(clave)
            return cache[clave]
        pdf = funcion(*args, **kwargs)
        if len(pdf) <= 2_000_000:
            cache[clave] = pdf
            cache.move_to_end(clave)
            while len(cache) > 8 or sum(map(len, cache.values())) > 6_000_000:
                cache.popitem(last=False)
        return pdf
    return obtener


def texto_seguro(valor):
    if valor is None or valor == "":
        return "No registrado"

    if isinstance(valor, bool):
        return "Sí" if valor else "No"

    if isinstance(valor, dict):
        valor = "\n".join(
            f"{campo}: {contenido}"
            for campo, contenido in valor.items()
        )

    elif isinstance(valor, (list, tuple)):
        valor = "\n".join(
            str(elemento)
            for elemento in valor
        )

    return escape(
        str(valor)
    ).replace("\n", "<br/>")


def pie_pagina(canvas, doc):
    ancho, alto = letter

    canvas.saveState()

    canvas.setStrokeColor(AMARILLO)
    canvas.setLineWidth(1.5)

    canvas.line(
        40, 48,
        ancho - 40, 48
    )

    canvas.setFillColor(AZUL)
    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        40, 34,
        "ElectraSafety Consultores | Electra Safe 360"
    )

    canvas.drawRightString(
        ancho - 40, 34,
        f"Página {doc.page}"
    )

    canvas.setFont("Helvetica", 7)

    canvas.drawString(
        40, 22,
        "Documento académico de apoyo técnico"
    )

    canvas.restoreState()


def encabezado_pagina(canvas, doc):
    ancho, alto = letter

    canvas.saveState()

    canvas.setFillColor(AZUL)

    canvas.rect(
        0,
        alto - 82,
        ancho,
        82,
        fill=1,
        stroke=0
    )

    if LOGO.exists():
        try:
            imagen = ImageReader(str(LOGO))

            w, h = imagen.getSize()

            factor = min(
                140 / w,
                55 / h
            )

            canvas.drawImage(
                imagen,
                40,
                alto - 68,
                width=w * factor,
                height=h * factor,
                mask="auto"
            )

        except Exception:
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 14)

            canvas.drawString(
                40,
                alto - 43,
                "Electra Safe 360"
            )

    else:
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 14)

        canvas.drawString(
            40,
            alto - 43,
            "Electra Safe 360"
        )

    canvas.setFillColor(colors.white)

    canvas.setFont(
        "Helvetica-Bold", 11
    )

    canvas.drawRightString(
        ancho - 40,
        alto - 33,
        "ElectraSafety Consultores"
    )

    canvas.setFont(
        "Helvetica", 9
    )

    canvas.drawRightString(
        ancho - 40,
        alto - 49,
        "Gestión de seguridad eléctrica"
    )

    canvas.setFillColor(AMARILLO)

    canvas.rect(
        0,
        alto - 86,
        ancho,
        4,
        fill=1,
        stroke=0
    )

    canvas.restoreState()

    pie_pagina(canvas, doc)


def generar_pdf(titulo, proyecto, secciones, referencia=""):
    proyecto = proyecto or {}
    cliente = proyecto.get("nombre_cliente")
    if cliente is None and proyecto.get("cliente_id") is not None:
        clientes = consultar("clientes")
        cliente = next(
            (c.get("nombre_empresa") for c in clientes if c["id"] == proyecto["cliente_id"]),
            None
        )

    informacion = {
        "Cliente": cliente,
        "Proyecto": proyecto.get("nombre"),
        "Código del proyecto": proyecto.get("codigo"),
        "Fecha de emisión": datetime.now().strftime("%d/%m/%Y")
    }
    return _generar_pdf(titulo, informacion, secciones, referencia, bool(proyecto))


@cache_pdf
def _generar_pdf(titulo, informacion, secciones, referencia, mostrar_proyecto):
    memoria = BytesIO()

    doc = SimpleDocTemplate(
        memoria,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=105,
        bottomMargin=65,
        title=str(titulo),
        author="ElectraSafety Consultores",
        subject="Gestión de seguridad eléctrica"
    )

    estilos = getSampleStyleSheet()

    estilos.add(
        ParagraphStyle(
            name="TituloElectra",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=23,
            textColor=AZUL,
            alignment=TA_CENTER,
            spaceAfter=18
        )
    )

    estilos.add(
        ParagraphStyle(
            name="SeccionElectra",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=AZUL,
            spaceBefore=12,
            spaceAfter=8,
            keepWithNext=True
        )
    )

    estilos.add(
        ParagraphStyle(
            name="CeldaElectra",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            splitLongWords=True
        )
    )

    estilos.add(
        ParagraphStyle(
            name="NotaElectra",
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=colors.HexColor(
                "#475569"
            ),
            spaceAfter=8
        )
    )

    elementos = []

    elementos.append(
        Paragraph(
            texto_seguro(titulo),
            estilos["TituloElectra"]
        )
    )

    def agregar_tabla(campos):
        if not campos:
            return

        if not isinstance(campos, dict):
            campos = {
                "Información": campos
            }

        filas = []

        for nombre, valor in campos.items():
            filas.append([
                Paragraph(
                    "<b>"
                    + texto_seguro(nombre)
                    + "</b>",
                    estilos["CeldaElectra"]
                ),
                Paragraph(
                    texto_seguro(valor),
                    estilos["CeldaElectra"]
                )
            ])

        tabla = Table(
            filas,
            colWidths=[
                (doc.width - 12) * 0.30,
                (doc.width - 12) * 0.70
            ],
            hAlign="LEFT",
            splitByRow=1,
            splitInRow=1
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    GRIS
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDE
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        elementos.append(tabla)
        elementos.append(
            Spacer(1, 10)
        )

    if mostrar_proyecto:
        elementos.append(Paragraph("Identificación del proyecto", estilos["SeccionElectra"]))
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
                estilos["NotaElectra"]
            )
        )

    elementos.append(
        Spacer(1, 15)
    )

    elementos.append(
        Paragraph(
            "Documento académico de apoyo. "
            "No constituye una autorización "
            "de trabajo ni sustituye la revisión "
            "de una persona calificada.",
            estilos["NotaElectra"]
        )
    )

    doc.build(
        elementos,
        onFirstPage=encabezado_pagina,
        onLaterPages=encabezado_pagina
    )

    memoria.seek(0)

    return memoria.getvalue()
