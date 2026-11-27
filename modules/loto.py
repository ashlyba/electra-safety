import streamlit as st
import pandas as pd

from database import consultar, insertar, eliminar

from modules.comunes import (
    seleccionar_proyecto,
    advertencia_tecnica,
    mostrar_aviso,
    notificar
)

from modules.documentos import administrar_documentos

from modules.loto_recursos import (
    imagen_svg,
    generar_catalogo_pdf,
    generar_loto_pdf
)


CATALOGO = [
    {
        "ID": "candado",
        "Nombre": "Candado de seguridad",
        "Función": "Restringir la operación no autorizada.",
        "Aplicación": "Puntos y dispositivos de aislamiento.",
        "Compatibilidad": "Diámetro del arco y dimensiones del dispositivo.",
        "Selección": "Verificar identificación individual y resistencia.",
        "Limitaciones": "No sustituye la verificación del aislamiento."
    },
    {
        "ID": "pinza",
        "Nombre": "Pinza de bloqueo múltiple",
        "Función": "Permitir la instalación de varios candados.",
        "Aplicación": "Procedimientos con varios trabajadores.",
        "Compatibilidad": "Dimensiones y capacidad de candados.",
        "Selección": "Considerar cantidad de participantes.",
        "Limitaciones": "No exceder la capacidad del fabricante."
    },
    {
        "ID": "interruptor",
        "Nombre": "Bloqueador de interruptores",
        "Función": "Restringir el accionamiento del interruptor.",
        "Aplicación": "Interruptores automáticos compatibles.",
        "Compatibilidad": "Marca, modelo y dimensiones.",
        "Selección": "Consultar especificaciones del interruptor.",
        "Limitaciones": "No todos los dispositivos son universales."
    },
    {
        "ID": "enchufe",
        "Nombre": "Bloqueador de enchufes",
        "Función": "Impedir la reconexión no autorizada.",
        "Aplicación": "Equipos alimentados mediante enchufe.",
        "Compatibilidad": "Tamaño y configuración del enchufe.",
        "Selección": "Verificar dimensiones y sistema de cierre.",
        "Limitaciones": "Considerar otras fuentes de energía."
    },
    {
        "ID": "valvula",
        "Nombre": "Bloqueador de válvulas",
        "Función": "Restringir la operación de válvulas.",
        "Aplicación": "Energías hidráulicas y neumáticas.",
        "Compatibilidad": "Tipo y diámetro de válvula.",
        "Selección": "Verificar configuración del dispositivo.",
        "Limitaciones": "No elimina por sí mismo la energía residual."
    },
    {
        "ID": "caja",
        "Nombre": "Caja de bloqueo grupal",
        "Función": "Gestionar las llaves de los puntos de aislamiento.",
        "Aplicación": "Trabajos con múltiples participantes.",
        "Compatibilidad": "Capacidad y mecanismo de cierre.",
        "Selección": "Considerar cantidad de trabajadores y llaves.",
        "Limitaciones": "Requiere un procedimiento grupal establecido."
    }
]


DOCUMENTACION_FABRICANTE = (
    "Catálogo técnico Brady de bloqueo y etiquetado "
    "(https://www.onlineelec.com/brands/brady/lockout_tagout/pdf/LOTO_Catalog.pdf). "
    "Consultar la ficha e instrucciones vigentes del modelo instalado."
)

APLICACIONES = {
    "candado": ("Cerrar el arco en un punto de bloqueo compatible.", "Orificio del desconectador, adaptador, pinza o caja según diseño.", "Brady, familias de candados de seguridad"),
    "pinza": ("Cerrar la mordaza sobre la orejeta del punto de bloqueo.", "Orificios de la pinza para los candados personales.", "Brady 65375"),
    "interruptor": ("Encajar el adaptador compatible sobre la palanca en posición de apertura.", "Orificio del adaptador; el candado impide liberar el mecanismo.", "Brady 65396 / 65397"),
    "enchufe": ("Alojar la clavija desconectada dentro de la carcasa.", "Punto de cierre de la carcasa; la etiqueta identifica el bloqueo.", "Brady PLO23"),
    "valvula": ("Cubrir el volante con un bloqueador compatible en la posición definida por el procedimiento.", "Orejeta de cierre de la cubierta; controlar la presión por separado.", "Brady 64057"),
    "caja": ("Depositar las llaves de los bloqueos de aislamiento dentro de la caja grupal.", "Cada participante usa su candado personal en un punto individual de la caja.", "Brady 65699"),
    "seccionador": ("Identificar el mecanismo bloqueable del seccionador en posición abierta según su manual.", "Orejeta prevista por el fabricante; verificar la compatibilidad con el arco del candado.", "Manual de instalación y operación del seccionador específico")
}

CATALOGO.append({
    "ID": "seccionador", "Nombre": "Bloqueo de seccionador",
    "Función": "Impedir que el medio de desconexión se cierre.",
    "Aplicación": "Seccionador con mecanismo bloqueable.",
    "Compatibilidad": "Posición y dimensiones de la orejeta y del candado.",
    "Selección": "Documentar el fabricante, modelo y referencia del seccionador.",
    "Limitaciones": "Confirmar aislamiento y la posición abierta mediante el procedimiento."
})
for dispositivo in CATALOGO:
    colocacion, fijacion, referencia = APLICACIONES[dispositivo["ID"]]
    dispositivo.update({
        "Colocación": colocacion, "Fijación": fijacion,
        "Candado y etiqueta": "Identificar a quien coloca el dispositivo y usar la etiqueta conforme al procedimiento.",
        "Referencia del fabricante": referencia
    })


POLITICA = {
    "1. Información general": [
        "Identificación",
        "Objetivo",
        "Alcance",
        "Equipos incluidos",
        "Documentación, diagramas y revisión"
    ],
    "2. Responsabilidades": [
        "Responsable del programa",
        "Personal autorizado",
        "Personal afectado",
        "Capacitación y auditoría",
        "Responsable del aislamiento, verificación y cierre",
        "Modalidad simple o compleja y persona encargada"
    ],
    "3. Planificación y control": [
        "Identificación de fuentes de energía",
        "Notificación al personal",
        "Parada del equipo",
        "Puntos y medios de aislamiento",
        "Dispositivos de bloqueo y etiquetado",
        "Aplicación de dispositivos y medidas adicionales",
        "Dispositivos específicos del proyecto y sus referencias",
        "Control de energía almacenada",
        "Verificación de aislamiento y ausencia de tensión",
        "Instrumento, EPP y registro de prueba",
        "Tensiones inducidas y puesta a tierra temporal"
    ],
    "4. Situaciones especiales": [
        "Bloqueo grupal",
        "Cambio de turno",
        "Retiro excepcional de dispositivos",
        "Contratistas",
        "Registro de participantes y transferencia de protección",
        "Liberación temporal para pruebas o posicionamiento"
    ],
    "5. Restitución del servicio": [
        "Inspección previa",
        "Retiro controlado de dispositivos",
        "Notificación y restitución",
        "Responsable de revisión",
        "Actualización y disponibilidad del procedimiento"
    ]
}


AYUDAS_POLITICA = {
    "Identificación de fuentes de energía": "Usa diagramas actualizados o un medio equivalente. Incluye fuentes principales, secundarias, retorno y energías no eléctricas.",
    "Puntos y medios de aislamiento": "Identifica el medio de desconexión de cada fuente y la forma de confirmar su posición. Distingue medios de desconexión de pulsadores y selectores.",
    "Modalidad simple o compleja y persona encargada": "Aplica 120.5(A)(4) o (5). Para LOTO complejo, registra el plan escrito y la persona encargada.",
    "Aplicación de dispositivos y medidas adicionales": "Si el diseño impide el candado y se usa etiquetado por sí solo, fundamenta la condición e indica la medida adicional y la responsabilidad de las personas expuestas.",
    "Dispositivos específicos del proyecto y sus referencias": "Registra otros dispositivos, modelo, compatibilidad, colocación, fijación e instrucciones del fabricante.",
    "Control de energía almacenada": "Documenta energía eléctrica y no eléctrica, tratamiento y control de reacumulación según 120.5(B)(2) y 120.6.",
    "Verificación de aislamiento y ausencia de tensión": "Documenta la comprobación de no rearranque y de ausencia de tensión en cada punto de trabajo según 120.5(B)(5)–(6) y 120.6(7).",
    "Instrumento, EPP y registro de prueba": "Indica clasificación del instrumento, quién verifica, protección y prueba antes y después en fuente conocida, o fundamenta la excepción aplicable.",
    "Tensiones inducidas y puesta a tierra temporal": "Indica si corresponde aplicar 120.6(8)–(9), con el criterio documentado.",
    "Capacitación y auditoría": "Registra auditoría del programa cada 3 años como máximo y de los procedimientos cada año como máximo por una persona calificada, según 110.3(L)(3)–(4).",
    "Bloqueo grupal": "Describe el control de llaves, dispositivos individuales y registro de participantes.",
    "Retiro excepcional de dispositivos": "Documenta el procedimiento del empleador, el intento de localizar a quien lo instaló y la notificación antes de que vuelva al trabajo.",
    "Inspección previa": "Registra pruebas e inspección visual, retiro de elementos temporales y comprobación de que las personas están fuera de la exposición.",
    "Notificación y restitución": "Identifica quién comunica el retorno y quién restituye conforme a la secuencia autorizada del procedimiento.",
    "Liberación temporal para pruebas o posicionamiento": "Identifica la persona calificada y los pasos de 120.5(B)(13)–(14) cuando corresponda."
}


def mostrar_catalogo():

    st.subheader("Catálogo de dispositivos LOTO")

    st.caption(
        "Ilustraciones esquemáticas de referencia."
    )

    st.markdown(
        "[Catálogo técnico Brady de bloqueo y etiquetado]"
        "(https://www.onlineelec.com/brands/brady/lockout_tagout/pdf/LOTO_Catalog.pdf)"
    )
    st.caption("Consulta la ficha e instrucciones vigentes del modelo instalado.")

    buscar = st.text_input(
        "Buscar dispositivo",
        placeholder="Ejemplo: candado"
    )

    dispositivos = [
        d for d in CATALOGO
        if buscar.lower() in d["Nombre"].lower()
    ]

    seleccion = st.multiselect(
        "Dispositivos para incluir en el catálogo PDF",
        [d["Nombre"] for d in CATALOGO],
        default=[d["Nombre"] for d in CATALOGO]
    )

    for dispositivo in dispositivos:

        with st.container(border=True):

            c1, c2 = st.columns([1, 2])

            with c1:

                st.image(
                    imagen_svg(dispositivo["ID"]),
                    use_container_width=True
                )

            with c2:

                st.subheader(dispositivo["Nombre"])

                for campo, valor in dispositivo.items():

                    if campo not in ["ID", "Nombre"]:

                        st.write(
                            f"**{campo}:** {valor}"
                        )

    elegidos = [
        d for d in CATALOGO
        if d["Nombre"] in seleccion
    ]

    if elegidos:

        st.download_button(
            "Descargar catálogo ilustrado PDF",
            generar_catalogo_pdf(elegidos, DOCUMENTACION_FABRICANTE),
            "catalogo_LOTO.pdf",
            "application/pdf",
            type="primary",
            use_container_width=True,
            on_click="ignore",
        )


def mostrar_etiquetas(proyecto):

    mostrar_aviso("loto_etiquetas")

    st.subheader("Generador de etiquetas LOTO")

    with st.form(f"form_etiqueta_loto_{proyecto['id']}"):

        c1, c2 = st.columns(2)

        with c1:

            responsable = st.text_input(
                "Nombre del responsable"
            )

            equipo = st.text_input(
                "Equipo bloqueado"
            )

            codigo = st.text_input(
                "Código de candado o etiqueta"
            )

        with c2:

            contacto = st.text_input(
                "Teléfono o contacto"
            )

            fecha = st.date_input(
                "Fecha de colocación"
            )

            ubicacion = st.text_input(
                "Ubicación del equipo"
            )

        motivo = st.text_area(
            "Motivo del bloqueo"
        )

        cantidad = st.number_input(
            "Cantidad de copias",
            min_value=1,
            max_value=30,
            value=1
        )

        generar = st.form_submit_button(
            "Generar vista previa",
            type="primary",
            use_container_width=True
        )

    clave = f"etiqueta_loto_{proyecto['id']}"

    if generar:

        if not all([
            responsable.strip(),
            equipo.strip(),
            codigo.strip(),
            motivo.strip()
        ]):

            st.error(
                "Completa los campos obligatorios."
            )

            st.session_state.pop(clave, None)

        else:

            st.session_state[clave] = {
                "Responsable": responsable.strip(),
                "Equipo": equipo.strip(),
                "Código": codigo.strip(),
                "Contacto": contacto,
                "Fecha": str(fecha),
                "Ubicación": ubicacion,
                "Motivo": motivo,
                "Tipo": "Etiqueta LOTO"
            }

    detalle = st.session_state.get(clave)

    if detalle:

        st.subheader("Vista previa")

        c1, c2 = st.columns([1, 1])

        with c1:

            with st.container(border=True):

                st.html("""
                <div style="
                    background:#B91C1C;
                    color:white;
                    text-align:center;
                    padding:20px;
                    font-size:30px;
                    font-weight:bold;
                    border-radius:6px;">
                    PELIGRO
                </div>
                """)

                st.title("NO OPERAR")

                for campo, valor in detalle.items():

                    if campo != "Tipo":

                        st.write(
                            f"**{campo}:** {valor}"
                        )

                st.warning(
                    "No retirar sin autorización."
                )

                st.caption(
                    "ElectraSafety Consultores"
                )

                st.caption(
                    "Muestra académica"
                )

        with c2:

            st.download_button(
                "Descargar etiqueta PDF",
                generar_loto_pdf(
                    [detalle] * int(cantidad)
                ),
                "etiqueta_LOTO.pdf",
                "application/pdf",
                use_container_width=True,
                on_click="ignore",
            )

            if st.button(
                "Guardar etiqueta",
                type="primary",
                use_container_width=True
            ):

                try:

                    registros = consultar(
                        "loto",
                        {"proyecto_id": proyecto["id"]}
                    )

                    duplicado = any(
                        (r.get("detalle") or {}).get(
                            "Tipo"
                        ) == "Etiqueta LOTO"
                        and
                        str(
                            (r.get("detalle") or {}).get(
                                "Código", ""
                            )
                        ).strip().lower()
                        == detalle["Código"].lower()
                        for r in registros
                    )

                    if duplicado:

                        st.warning(
                            "Ya existe una etiqueta "
                            "con este código."
                        )

                    else:

                        respuesta = insertar(
                            "loto",
                            {
                                "proyecto_id": proyecto["id"],
                                "detalle": detalle
                            }
                        )

                        if respuesta:

                            notificar(
                                "loto_etiquetas",
                                "Etiqueta registrada exitosamente."
                            )

                        else:

                            st.error(
                                "No se confirmó el guardado."
                            )

                except Exception as error:

                    st.error(str(error))

    st.divider()

    st.subheader("Etiquetas registradas")

    registros = consultar(
        "loto",
        {"proyecto_id": proyecto["id"]}
    )

    registros = [
        r for r in registros
        if (r.get("detalle") or {}).get(
            "Tipo"
        ) == "Etiqueta LOTO"
    ]

    if not registros:

        st.info(
            "No hay etiquetas registradas."
        )

        return

    st.dataframe(
        pd.DataFrame([
            r["detalle"] for r in registros
        ]),
        hide_index=True,
        use_container_width=True
    )

    opciones = {
        r["id"]: r for r in registros
    }

    seleccion = st.multiselect(
        "Seleccionar etiquetas para imprimir",
        list(opciones),
        format_func=lambda x: (
            opciones[x]["detalle"].get("Código", "")
            + " | "
            + opciones[x]["detalle"].get("Equipo", "")
        )
    )

    if seleccion:

        st.download_button(
            "Descargar etiquetas seleccionadas",
            generar_loto_pdf([
                opciones[x]["detalle"]
                for x in seleccion
            ]),
            "lote_etiquetas_LOTO.pdf",
            "application/pdf",
            on_click="ignore",
        )

    with st.expander("Eliminar etiqueta"):

        etiqueta_id = st.selectbox(
            "Seleccionar etiqueta",
            list(opciones),
            format_func=lambda x: (
                opciones[x]["detalle"].get("Código", "")
            )
        )

        confirmar = st.checkbox(
            "Confirmo que deseo eliminar la etiqueta"
        )

        if st.button(
            "Eliminar etiqueta",
            disabled=not confirmar
        ):

            if eliminar("loto", etiqueta_id):

                notificar(
                    "loto_etiquetas",
                    "Etiqueta eliminada correctamente."
                )


def mostrar():

    st.title("06. Bloqueo y etiquetado LOTO")

    st.write(
        "Herramientas para la planificación y "
        "documentación del control de energías peligrosas."
    )

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

        mostrar_catalogo()

    with tab2:
        st.caption(
            "Documenta la secuencia del artículo 120 para el equipo y proyecto. "
            "El Anexo G ilustra un programa. Justifica las situaciones que no correspondan."
        )
        administrar_documentos(
            "loto",
            proyecto,
            "Política y procedimiento LOTO",
            POLITICA,
            "NFPA 70E 2027: 120.2 a 120.6 y 110.3(L)(3)–(4). Anexo G informativo.",
            tipo="Política LOTO", ayudas=AYUDAS_POLITICA
        )

    with tab3:

        mostrar_etiquetas(proyecto)
