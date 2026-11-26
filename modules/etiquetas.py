
import streamlit as st
import pandas as pd
import math

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

from database import consultar, insertar, eliminar

from modules.comunes import (
    seleccionar_proyecto,
    mostrar_aviso,
    notificar,
    advertencia_tecnica
)


def normalizar(valor):

    return " ".join(str(valor or "").split()).casefold()


def positivo(valor):

    try:

        numero = float(valor)

        return math.isfinite(numero) and numero > 0

    except (ValueError, TypeError):

        return False


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
        fontSize=10,
        leading=13
    )

    encabezado = ParagraphStyle(
        "EncabezadoEtiqueta",
        fontSize=22,
        leading=26,
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
                    "<b>PELIGRO DE ARCO Y CHOQUE ELÉCTRICO</b>",
                    normal
                )
            ],
            [
                Paragraph(
                    '<font color="#B91C1C">'
                    '<b>MUESTRA ACADÉMICA - NO UTILIZAR EN CAMPO</b>'
                    '</font>',
                    normal
                )
            ]
        ]

        for campo, valor in detalle.items():

            if valor is None or valor == "":
                continue

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
            colWidths=[500],
            hAlign="CENTER"
        )

        tabla.setStyle(TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, 0),
                colors.HexColor("#E97719")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                1.5,
                colors.black
            ),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12)
        ]))

        elementos.append(
            KeepTogether([tabla, Spacer(1, 18)])
        )

    doc.build(elementos)

    return memoria.getvalue()


def preparar_etiqueta(
    detalle,
    referencia,
    revision,
    responsable
):

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
        "Método": "Categorías de EPP",
        "Categoría de EPP": detalle.get("Categoría"),
        "Origen": "Evaluación interna - Módulo 4",
        "Identificación de evaluación": str(referencia),
        "Revisión": revision,
        "Referencia": detalle.get("Referencia arco"),
        "Responsable de preparación": responsable,
        "Fecha de preparación": str(date.today()),
        "Estado": "Borrador académico"
    }


def vista_previa(detalle):

    with st.container(border=True):

        st.html("""
        <div style="
            background:#E97719;
            color:black;
            text-align:center;
            padding:14px;
            font-size:25px;
            font-weight:bold;
            border-radius:5px;">
            ADVERTENCIA
        </div>
        """)

        st.markdown(
            "### PELIGRO DE ARCO Y CHOQUE ELÉCTRICO"
        )

        st.error(
            "MUESTRA ACADÉMICA — NO UTILIZAR EN CAMPO"
        )

        for campo, valor in detalle.items():

            if valor is not None and valor != "":

                st.write(f"**{campo}:** {valor}")

        st.caption("ElectraSafety Consultores")


def identidad(detalle):

    return (
        normalizar(detalle.get("Equipo")),
        normalizar(detalle.get("Ubicación")),
        normalizar(detalle.get("Revisión"))
    )


def guardar_etiquetas(proyecto, etiquetas):

    existentes = consultar(
        "etiquetas",
        {"proyecto_id": proyecto["id"]}
    )

    claves = {
        identidad(r.get("detalle") or {})
        for r in existentes
    }

    cantidad = 0
    duplicadas = 0
    errores = []

    for etiqueta in etiquetas:

        clave = identidad(etiqueta)

        if clave in claves:

            duplicadas += 1
            continue

        try:

            respuesta = insertar(
                "etiquetas",
                {
                    "proyecto_id": proyecto["id"],
                    "detalle": etiqueta
                }
            )

            if respuesta:

                cantidad += 1
                claves.add(clave)

            else:

                errores.append(
                    str(etiqueta.get("Equipo", "Equipo"))
                )

        except Exception as error:

            errores.append(str(error))

    if errores:

        st.error(
            "No se pudieron guardar algunos registros."
        )

        st.write(errores)

    if duplicadas:

        st.warning(
            f"{duplicadas} etiquetas ya existen "
            "para el mismo equipo, ubicación y revisión."
        )

    if cantidad:

        notificar(
            "etiquetas",
            f"{cantidad} etiquetas registradas exitosamente. "
            f"Duplicadas omitidas: {duplicadas}. "
            f"Errores: {len(errores)}."
        )


def mostrar_internas(proyecto):

    st.subheader("Etiquetas desde evaluaciones internas")

    registros = consultar(
        "arco_electrico",
        {"proyecto_id": proyecto["id"]}
    )

    validos = []

    for r in registros:

        d = r.get("detalle") or {}

        if (
            d.get("Método aplicable") == "Sí"
            and positivo(d.get("Tensión (V)"))
            and positivo(d.get("Frontera de arco"))
            and str(d.get("Categoría")) in ["1", "2", "3", "4"]
            and str(d.get("Equipo") or "").strip()
            and str(d.get("Referencia arco") or "").strip()
        ):

            validos.append(r)

    c1, c2 = st.columns(2)

    with c1:

        buscar = st.text_input(
            "Buscar equipo o ubicación",
            key="etiquetas_internas_buscar"
        )

    with c2:

        categoria = st.selectbox(
            "Categoría de EPP",
            ["Todas", "1", "2", "3", "4"],
            key="etiquetas_internas_categoria"
        )

    opciones = {}

    for r in validos:

        d = r.get("detalle") or {}

        texto = (
            str(d.get("Equipo", ""))
            + " "
            + str(d.get("Ubicación", ""))
        )

        if normalizar(buscar) not in normalizar(texto):
            continue

        if (
            categoria != "Todas"
            and str(d.get("Categoría")) != categoria
        ):

            continue

        opciones[r["id"]] = r

    seleccion = st.multiselect(
        "Seleccionar equipos",
        list(opciones),
        format_func=lambda x: (
            str(opciones[x]["detalle"].get("Equipo", ""))
            + " | "
            + str(x)[:8]
        )
    )

    revision = st.text_input(
        "Identificación de revisión",
        value="Rev. 01",
        key="revision_interna"
    )

    responsable = st.text_input(
        "Responsable de preparación",
        key="responsable_interno"
    )

    if not seleccion:

        st.info(
            "Selecciona evaluaciones completas del módulo 4 "
            "con el método de categorías aplicable."
        )

        return

    if not revision.strip() or not responsable.strip():

        st.warning(
            "Completa la revisión y el responsable."
        )

        return

    etiquetas = [
        preparar_etiqueta(
            opciones[x]["detalle"],
            x,
            revision.strip(),
            responsable.strip()
        )
        for x in seleccion
    ]

    st.caption(
        "Las etiquetas recuperadas son borradores académicos. "
        "Los datos requieren revisión técnica."
    )

    for etiqueta in etiquetas:

        vista_previa(etiqueta)

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(
            "Descargar etiquetas PDF",
            generar_etiquetas(etiquetas),
            "etiquetas_internas.pdf",
            "application/pdf",
            use_container_width=True
        )

    with c2:

        if st.button(
            "Guardar etiquetas",
            type="primary",
            key="guardar_internas",
            use_container_width=True
        ):

            guardar_etiquetas(proyecto, etiquetas)


def mostrar_externas(proyecto):

    st.subheader("Etiquetas con datos externos")

    st.info(
        "Utiliza datos procedentes de un estudio eléctrico "
        "documentado. Este formulario no calcula "
        "la energía incidente ni determina el EPP."
    )

    metodo = st.radio(
        "Método utilizado en la evaluación",
        [
            "Categorías de EPP",
            "Energía incidente"
        ],
        horizontal=True,
        key="metodo_externo"
    )

    with st.form(f"externa_{metodo}"):

        c1, c2 = st.columns(2)

        with c1:

            equipo = st.text_input("Nombre del equipo")

            ubicacion = st.text_input("Ubicación")

            tension = st.number_input(
                "Tensión nominal (V)",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

            sistema = st.selectbox(
                "Sistema eléctrico",
                ["CA", "CC"]
            )

        with c2:

            frontera = st.number_input(
                "Frontera de arco eléctrico (m)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.3f"
            )

            revision = st.text_input(
                "Identificación de revisión",
                value="Rev. 01"
            )

            fecha_estudio = st.date_input(
                "Fecha del estudio",
                max_value=date.today()
            )

        categoria = None
        energia = None
        distancia = None
        proteccion = None

        if metodo == "Categorías de EPP":

            categoria = st.selectbox(
                "Categoría determinada por el estudio",
                [1, 2, 3, 4]
            )

        else:

            energia = st.number_input(
                "Energía incidente (cal/cm²)",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

            distancia = st.number_input(
                "Distancia de trabajo (mm)",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

            proteccion = st.text_input(
                "Protección especificada en el estudio"
            )

        st.subheader("Trazabilidad y revisión")

        fuente = st.text_input(
            "Nombre o código del informe técnico"
        )

        referencia = st.text_input(
            "Página, sección o referencia específica"
        )

        autor = st.text_input(
            "Autor o empresa responsable del estudio"
        )

        revisor = st.text_input(
            "Responsable de revisión documental"
        )

        fecha_revision = st.date_input(
            "Fecha de revisión",
            max_value=date.today()
        )

        observaciones = st.text_area(
            "Observaciones de la revisión"
        )

        confirmar = st.checkbox(
            "Confirmo que los datos fueron transcritos "
            "de la fuente identificada y revisados "
            "para fines académicos."
        )

        generar = st.form_submit_button(
            "Generar vista previa",
            type="primary",
            use_container_width=True
        )

    clave = f"etiqueta_externa_{proyecto['id']}_{metodo}"

    if generar:

        st.session_state.pop(clave, None)

        completos = all([
            equipo.strip(),
            ubicacion.strip(),
            tension > 0,
            frontera > 0,
            revision.strip(),
            fuente.strip(),
            referencia.strip(),
            autor.strip(),
            revisor.strip(),
            observaciones.strip(),
            confirmar
        ])

        if metodo == "Energía incidente":

            completos = completos and all([
                energia > 0,
                distancia > 0,
                proteccion.strip()
            ])

        if not completos:

            st.error(
                "Completa todos los datos técnicos "
                "y la revisión documental."
            )

        elif fecha_revision < fecha_estudio:

            st.error(
                "La revisión no puede ser anterior al estudio."
            )

        else:

            detalle = {
                "Equipo": equipo.strip(),
                "Ubicación": ubicacion.strip(),
                "Tensión nominal": f"{tension:g} V {sistema}",
                "Frontera de arco": f"{frontera:g} m",
                "Método": metodo
            }

            if metodo == "Categorías de EPP":

                detalle["Categoría de EPP"] = categoria

            else:

                detalle["Energía incidente"] = (
                    f"{energia:g} cal/cm²"
                )

                detalle["Distancia de trabajo"] = (
                    f"{distancia:g} mm"
                )

                detalle["Protección especificada"] = proteccion

            detalle.update({
                "Origen": "Estudio externo",
                "Fuente técnica": fuente.strip(),
                "Referencia": referencia.strip(),
                "Autor del estudio": autor.strip(),
                "Fecha del estudio": str(fecha_estudio),
                "Revisión": revision.strip(),
                "Responsable de revisión": revisor.strip(),
                "Fecha de revisión": str(fecha_revision),
                "Observaciones": observaciones.strip(),
                "Estado": "Revisado documentalmente - académico"
            })

            st.session_state[clave] = detalle

    detalle = st.session_state.get(clave)

    if detalle:

        st.subheader("Vista previa")

        st.caption(
            "La vista previa corresponde a los últimos datos "
            "enviados mediante Generar vista previa."
        )

        vista_previa(detalle)

        c1, c2 = st.columns(2)

        with c1:

            st.download_button(
                "Descargar etiqueta PDF",
                generar_etiquetas([detalle]),
                "etiqueta_externa.pdf",
                "application/pdf",
                use_container_width=True
            )

        with c2:

            if st.button(
                "Guardar etiqueta externa",
                type="primary",
                use_container_width=True
            ):

                guardar_etiquetas(proyecto, [detalle])


def mostrar_guardadas(proyecto):

    st.subheader("Etiquetas registradas")

    registros = consultar(
        "etiquetas",
        {"proyecto_id": proyecto["id"]}
    )

    if not registros:

        st.info("No hay etiquetas guardadas.")
        return

    c1, c2, c3 = st.columns(3)

    with c1:

        buscar = st.text_input(
            "Buscar equipo o ubicación",
            key="buscar_guardadas"
        )

    with c2:

        origen = st.selectbox(
            "Origen",
            [
                "Todos",
                "Evaluación interna",
                "Estudio externo"
            ]
        )

    with c3:

        metodo = st.selectbox(
            "Método",
            [
                "Todos",
                "Categorías de EPP",
                "Energía incidente"
            ]
        )

    opciones = {}

    for r in registros:

        d = r.get("detalle") or {}

        texto = " ".join([
            str(d.get("Equipo", "")),
            str(d.get("Ubicación", ""))
        ])

        origen_actual = d.get(
            "Origen",
            "Evaluación interna - Módulo 4"
        )

        metodo_actual = d.get(
            "Método",
            "Categorías de EPP"
        )

        if normalizar(buscar) not in normalizar(texto):
            continue

        if origen != "Todos" and not origen_actual.startswith(origen):
            continue

        if metodo != "Todos" and metodo_actual != metodo:
            continue

        opciones[r["id"]] = r

    if not opciones:

        st.info("No hay resultados para los filtros.")
        return

    st.dataframe(
        pd.DataFrame([
            r.get("detalle") or {}
            for r in opciones.values()
        ]),
        hide_index=True,
        use_container_width=True
    )

    def nombre_etiqueta(x):

        d = opciones[x].get("detalle") or {}

        return (
            str(d.get("Equipo", ""))
            + " | "
            + str(d.get("Ubicación", ""))
            + " | "
            + str(d.get("Revisión", ""))
        )

    individual = st.selectbox(
        "Consultar etiqueta individual",
        list(opciones),
        format_func=nombre_etiqueta
    )

    with st.expander("Vista previa individual"):

        detalle = opciones[individual].get("detalle") or {}

        vista_previa(detalle)

        st.download_button(
            "Descargar etiqueta individual",
            generar_etiquetas([detalle]),
            "etiqueta_individual.pdf",
            "application/pdf"
        )

    todas = st.checkbox(
        "Seleccionar todas las etiquetas filtradas"
    )

    if todas:

        seleccion = list(opciones)

    else:

        seleccion = st.multiselect(
            "Seleccionar etiquetas para imprimir",
            list(opciones),
            format_func=nombre_etiqueta
        )

    if seleccion:

        st.download_button(
            f"Descargar lote de {len(seleccion)} etiquetas",
            generar_etiquetas([
                opciones[x].get("detalle") or {}
                for x in seleccion
            ]),
            "lote_etiquetas_electricas.pdf",
            "application/pdf",
            type="primary",
            use_container_width=True
        )

    with st.expander("Eliminar etiqueta"):

        eliminar_id = st.selectbox(
            "Etiqueta que desea eliminar",
            list(opciones),
            format_func=nombre_etiqueta,
            key="eliminar_etiqueta_id"
        )

        confirmar = st.checkbox(
            "Confirmo la eliminación permanente",
            key="confirmar_eliminar_etiqueta"
        )

        if st.button(
            "Eliminar etiqueta",
            disabled=not confirmar
        ):

            try:

                if eliminar("etiquetas", eliminar_id):

                    notificar(
                        "etiquetas",
                        "Etiqueta eliminada correctamente."
                    )

                else:

                    st.error("No se confirmó la eliminación.")

            except Exception as error:

                st.error(str(error))


def mostrar():

    st.title("05. Diseño e impresión de etiquetas")

    st.write(
        "Generación de etiquetas de advertencia eléctrica "
        "a partir de evaluaciones internas o estudios externos."
    )

    advertencia_tecnica()

    mostrar_aviso("etiquetas")

    proyecto = seleccionar_proyecto("etiquetas")

    if not proyecto:
        return

    tab1, tab2, tab3 = st.tabs([
        "Desde evaluación",
        "Datos externos",
        "Etiquetas guardadas"
    ])

    with tab1:

        mostrar_internas(proyecto)

    with tab2:

        mostrar_externas(proyecto)

    with tab3:

        mostrar_guardadas(proyecto)
