import streamlit as st
import pandas as pd

from datetime import datetime, timezone
from uuid import uuid4

from database import (
    consultar,
    insertar,
    actualizar,
    eliminar
)

from modules.comunes import (
    seleccionar_proyecto,
    mostrar_aviso,
    notificar,
    advertencia_tecnica
)

from modules.tablas_nfpa import (
    TABLA_CA,
    TAREAS_ARCO,
    REVISION_CRITERIOS,
    resultado_arco_vigente,
    probabilidad_arco,
    calcular_arco,
    limites_choque,
    clase_guante,
    PROTECCION_ARCO
)

from modules.guia_epp import mostrar_guia_epp
from modules.reportes import generar_pdf


def distancia_texto(valor):
    if valor is None:
        return "No especificado"

    if isinstance(valor, str):
        return valor

    return f"{valor} m"


def fecha_actual():
    return datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")


def presentar_resultado(detalle):
    st.subheader(
        "Protección contra arco eléctrico"
    )

    if resultado_arco_vigente(detalle):
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Categoría de EPP",
            detalle.get("Categoría", "—")
        )

        c2.metric(
            "Protección mínima",
            f"{detalle.get('Protección mínima')} cal/cm²"
        )

        c3.metric(
            "Frontera de arco",
            f"{detalle.get('Frontera de arco')} m"
        )

        st.info(
            "Coincidencia preliminar con una fila "
            "implementada del método de tablas."
        )

    else:
        st.warning(
            detalle.get(
                "Motivo",
                "Información insuficiente."
            ) or "Reevalúe este punto con los criterios actuales antes de reutilizar sus resultados."
        )

    st.subheader(
        "Protección contra choque eléctrico"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Aproximación limitada",
        detalle.get(
            "Aproximación limitada",
            "No determinada"
        )
    )

    c2.metric(
        "Aproximación restringida",
        detalle.get(
            "Aproximación restringida",
            "No determinada"
        )
    )

    c3.metric(
        "Clase orientativa de guante",
        detalle.get(
            "Clase de guante",
            "No determinada"
        )
    )

    st.caption(
        "La protección contra choque debe "
        "evaluarse independientemente de la "
        "protección contra arco eléctrico."
    )

    st.warning(
        "Los resultados son académicos y requieren "
        "validación normativa y revisión por una "
        "persona calificada."
    )


def formulario_evaluacion(
    proyecto,
    registro=None
):
    anterior = (
        registro.get("detalle") or {}
        if registro
        else {}
    )

    identificador = (
        str(registro["id"])
        if registro
        else "nuevo"
    )

    clave = (
        f"arco_{proyecto['id']}_{identificador}"
    )

    sistema_anterior = anterior.get(
        "Sistema", "CA"
    )

    sistema = st.radio(
        "Tipo de sistema",
        ["CA", "CC"],
        index=(
            1 if sistema_anterior == "CC"
            else 0
        ),
        horizontal=True,
        key=f"{clave}_sistema"
    )

    equipos = (
        list(TABLA_CA)
        if sistema == "CA"
        else ["Baterías y equipos de CC"]
    )

    equipo_anterior = anterior.get(
        "Tipo de equipo"
    )

    indice_equipo = (
        equipos.index(equipo_anterior)
        if equipo_anterior in equipos
        else 0
    )

    with st.form(f"{clave}_formulario"):
        st.subheader(
            "Identificación del punto"
        )

        c1, c2 = st.columns(2)

        nombre = c1.text_input(
            "Identificación del equipo *",
            value=anterior.get("Equipo", "")
        )

        ubicacion = c2.text_input(
            "Ubicación del equipo *",
            value=anterior.get("Ubicación", "")
        )

        equipo = st.selectbox(
            "Tipo y clasificación del equipo",
            equipos,
            index=indice_equipo
        )

        tarea = st.text_area(
            "Tarea que se realizará *",
            value=anterior.get("Tarea", "")
        )

        estado = st.selectbox(
            "Condición del equipo",
            [
                "Normal",
                "Anormal",
                "No determinada"
            ],
            index=[
                "Normal",
                "Anormal",
                "No determinada"
            ].index(
                anterior.get(
                    "Condición del equipo",
                    "No determinada"
                ) if anterior.get("Condición del equipo") in {"Normal", "Anormal"}
                else "No determinada"
            ),
            help="Para condición normal, verifica instalación, mantenimiento, capacidad de falla, uso conforme a fabricante, puertas y cubiertas aseguradas y ausencia de falla inminente."
        )

        fila_tarea = st.selectbox(
            "Fila normativa de la tarea "
            "(verifique todas sus condiciones)",
            [None] + list(range(len(TAREAS_ARCO))),
            format_func=lambda i: (
                "No determinada / otra tarea"
                if i is None
                else TAREAS_ARCO[i][0]
            ),
            index=next(
                (i + 1 for i, fila in enumerate(TAREAS_ARCO)
                 if fila[0] == anterior.get("Fila normativa de tarea")),
                0
            )
        )

        evidencia_tarea = st.text_area(
            "Justificación de correspondencia "
            "con la fila y condición de funcionamiento",
            value=anterior.get(
                "Justificación de tarea", ""
            )
        )

        st.subheader(
            "Parámetros eléctricos"
        )

        c1, c2 = st.columns(2)

        voltaje = c1.number_input(
            "Tensión nominal (V)",
            min_value=0.0,
            value=float(
                anterior.get("Tensión (V)") or 0
            )
        )

        corriente = c2.number_input(
            "Corriente de falla disponible (kA)",
            min_value=0.0,
            value=float(
                anterior.get(
                    "Corriente de falla (kA)"
                ) or 0
            ),
            format="%.3f"
        )

        tiempo = c1.number_input(
            "Tiempo de despeje (CA) o duración del arco (CC), en s",
            min_value=0.0,
            value=float(
                anterior.get("Tiempo (s)") or 0
            ),
            format="%.4f"
        )

        distancia = c2.number_input(
            "Distancia de trabajo (mm)",
            min_value=0.0,
            value=float(
                anterior.get(
                    "Distancia de trabajo (mm)"
                ) or 0
            )
        )

        tension_tarea = st.number_input(
            "Tensión de la tarea (V) para filas con umbral específico",
            min_value=0.0, value=float(anterior.get("Tensión de la tarea (V)") or 0),
            help="Completa en circuitos de control, baterías con separación especificada y desconexión exterior."
        )
        separacion = st.number_input(
            "Separación entre conductores (mm), si la fila de baterías lo requiere",
            min_value=0.0, value=float(anterior.get("Separación entre conductores (mm)") or 0)
        )
        tension_exposicion = st.number_input(
            "Tensión de exposición a choque (V CA RMS o V CC)",
            min_value=0.0, value=float(anterior.get("Tensión de exposición (V)") or 0),
            help="Usa la tensión de exposición documentada para orientar la clase del guante."
        )
        altitud = st.number_input(
            "Elevación del sitio (m s. n. m.)",
            value=anterior.get("Altitud (m)"),
            step=1,
            help="Requerida para informar el límite restringido del punto de trabajo."
        )

        movil = st.radio(
            "Tipo de parte energizada expuesta",
            [
                "Parte fija",
                "Conductor móvil",
                "Sin parte expuesta",
                "Exposición sin determinar"
            ],
            index={
                "Parte fija": 0, "Conductor móvil": 1,
                "Sin parte expuesta": 2, "Exposición sin determinar": 3
            }.get(anterior.get("Parte expuesta"), 3)
        )

        fuente = st.text_area(
            "Fuente de los datos eléctricos *",
            value=anterior.get(
                "Fuente de datos", ""
            ),
            placeholder=(
                "Estudio de cortocircuito, "
                "planos, curvas de protección "
                "y documentación técnica."
            )
        )

        st.subheader("Condiciones de aplicación")
        filas_mcc = [None, 2, 4]
        fila_mcc = st.selectbox(
            "Fila documentada para MCC clase 600 V",
            filas_mcc,
            index=filas_mcc.index(anterior.get("Fila MCC")) if anterior.get("Fila MCC") in filas_mcc else 0,
            format_func=lambda x: {None: "Sin selección", 2: "65 kA y 0,03 s", 4: "42 kA y 0,33 s"}[x],
            help="Completa este campo cuando ambas filas superen la comprobación numérica."
        )
        opciones_cc = ["Sin determinar", "Al aire libre, sin exposición a electrolito",
                       "Envolvente o posible exposición a electrolito", "Capacitores del artículo 360"]
        condicion_cc = st.selectbox(
            "Alcance de la evaluación de CC", opciones_cc,
            index=opciones_cc.index(anterior.get("Condición de CC")) if anterior.get("Condición de CC") in opciones_cc else 0,
            disabled=sistema != "CC",
            help="La herramienta automatiza la fila de CC al aire libre y sin exposición a electrolito. Otros casos requieren revisión técnica."
        )
        bases_ca = {"pendiente": "Sin determinar", "fase_fase": "Tensión nominal fase a fase",
                    "monofasico": "Sistema monofásico", "nota_e": "Rango 50–150 V, nota e"}
        base_anterior = anterior.get("Base de tensión CA")
        base_ca = st.selectbox(
            "Base de tensión para límites de choque en CA", list(bases_ca),
            index=list(bases_ca).index(base_anterior) if base_anterior in bases_ca else 0,
            format_func=bases_ca.get, disabled=sistema != "CA"
        )
        fase_tierra = st.number_input(
            "Tensión máxima fase a tierra (V) para monofásico o nota e",
            min_value=0.0, value=float(anterior.get("Tensión fase a tierra (V)") or 0),
            disabled=sistema != "CA"
        )
        st.caption("Use la tensión nominal del equipo para arco. Para choque, documente el conductor expuesto, la base de tensión y la elevación real.")

        requiere_epp = st.checkbox(
            "La evaluación previa determina "
            "que se requiere EPP contra arco.",
            value=anterior.get("Requiere EPP contra arco") is True
        )

        clasificacion = st.checkbox(
            "Se verificó la clasificación "
            "y el tipo de equipo.",
            value=anterior.get("Clasificación verificada") is True
        )

        normal_verificada = st.checkbox(
            "Para condición normal, confirmé los siete criterios de 110.2(B), excepción 1",
            value=anterior.get("Condición normal verificada") is True,
            help="Instalación, mantenimiento, clasificación de falla, uso según fabricante, puertas, cubiertas y ausencia de indicios de falla."
        )
        mantenimiento = st.checkbox(
            "Se verificó el estado y "
            "mantenimiento del equipo.",
            value=anterior.get("Mantenimiento verificado") is True
        )

        notas = st.checkbox(
            "Se revisaron las notas, condiciones y excepciones de la fila normativa.",
            value=anterior.get("Notas verificadas") is True,
            help="La aplicación mantiene la categoría de la fila sin aplicar reducciones opcionales por dispositivos limitadores."
        )

        solo_tablas = st.checkbox(
            "Se utilizará únicamente el método "
            "de categorías, sin combinarlo "
            "con energía incidente.",
            value=anterior.get("Método exclusivo de tablas") is True
        )

        evidencia = st.text_area(
            "Justificación y evidencia "
            "de las verificaciones",
            value=anterior.get(
                "Evidencia normativa", ""
            )
        )

        responsable = st.text_input(
            "Responsable de la evaluación",
            value=anterior.get(
                "Responsable", ""
            )
        )

        evaluar = st.form_submit_button(
            "Evaluar parámetros",
            type="primary",
            use_container_width=True
        )

    if evaluar:
        st.session_state.pop(
            f"{clave}_resultado", None
        )

        if not all([
            nombre.strip(),
            ubicacion.strip(),
            tarea.strip(),
            fuente.strip()
        ]):
            st.error(
                "Complete los campos obligatorios."
            )

            return

        arco = calcular_arco(
            sistema,
            equipo,
            voltaje,
            corriente,
            tiempo,
            distancia, fila_mcc=fila_mcc
        )

        probabilidad = probabilidad_arco(
            fila_tarea, estado, sistema, tension_tarea, separacion
        ) if estado != "Normal" or normal_verificada else None

        condiciones = all([
            probabilidad is True,
            bool(evidencia_tarea.strip()),
            bool(responsable.strip()),
            requiere_epp,
            clasificacion,
            mantenimiento,
            notas,
            solo_tablas,
            bool(evidencia.strip()),
            estado != "No determinada",
            sistema != "CC" or condicion_cc == "Al aire libre, sin exposición a electrolito"
        ])

        if not condiciones:
            arco = {
                "aplicable": False,
                "motivo": (
                    "No se documentaron todas "
                    "las condiciones previas "
                    "de aplicación del método."
                )
            }

        choque = limites_choque(
            sistema,
            voltaje,
            movil == "Conductor móvil",
            base_ca=base_ca if sistema == "CA" else None,
            fase_tierra=fase_tierra,
            altitud=altitud
        ) if (
            altitud is not None and movil in {"Parte fija", "Conductor móvil"}
            and (sistema != "CA" or base_ca != "pendiente")
        ) else None

        limitada = (
            distancia_texto(
                choque.get("limitada")
            )
            if choque
            else "No determinada"
        )

        restringida = (
            distancia_texto(
                choque.get("restringida")
            )
            if choque
            else "No determinada"
        )

        if movil == "Sin parte expuesta":
            limitada = restringida = "No aplica: sin partes energizadas expuestas"
        guante = (
            clase_guante(sistema, tension_exposicion)
            if movil in {"Parte fija", "Conductor móvil"} else None
        )

        categoria = arco.get(
            "categoria"
        )

        detalle = {
            "Versión de criterios de arco": REVISION_CRITERIOS,
            "Índice de fila de tarea": fila_tarea,
            "Condición normal verificada": normal_verificada,
            "Tensión de la tarea (V)": tension_tarea,
            "Separación entre conductores (mm)": separacion,
            "Tensión de exposición (V)": tension_exposicion,
            "Fila MCC": fila_mcc,
            "Condición de CC": condicion_cc if sistema == "CC" else None,
            "Base de tensión CA": base_ca if sistema == "CA" else None,
            "Tensión fase a tierra (V)": fase_tierra if sistema == "CA" else None,
            "Código del punto": anterior.get(
                "Código del punto"
            ) or (
                "AE-" + uuid4().hex[:8].upper()
            ),

            "Revisión": (
                int(
                    anterior.get("Revisión") or 0
                ) + 1
            ),

            "Fecha de revisión": fecha_actual(),

            "Equipo": nombre.strip(),

            "Tipo de equipo": equipo,

            "Ubicación": ubicacion.strip(),

            "Tarea": tarea.strip(),

            "Fila normativa de tarea": (
                TAREAS_ARCO[fila_tarea][0]
                if fila_tarea is not None
                else "No determinada"
            ),

            "Probabilidad de arco": (
                "Sí"
                if probabilidad is True
                else "No"
                if probabilidad is False
                else "No determinada"
            ),

            "Justificación de tarea":
                evidencia_tarea,

            "Condición del equipo": estado,

            "Sistema": sistema,

            "Tensión (V)": voltaje,

            "Corriente de falla (kA)": corriente,

            "Tiempo (s)": tiempo,

            "Distancia de trabajo (mm)": distancia,

            "Altitud (m)": altitud,

            "Parte expuesta": movil,

            "Fuente de datos": fuente,

            "Responsable": responsable,

            "Requiere EPP contra arco":
                requiere_epp,

            "Clasificación verificada":
                clasificacion,

            "Mantenimiento verificado":
                mantenimiento,

            "Notas verificadas": notas,

            "Método exclusivo de tablas":
                solo_tablas,

            "Evidencia normativa": evidencia,

            "Método aplicable": (
                "Sí" if arco["aplicable"]
                else "No"
            ),

            "Categoría": categoria,

            "Frontera de arco": arco.get(
                "frontera"
            ),

            "Protección mínima": (
                PROTECCION_ARCO.get(categoria)
            ),

            "Motivo": arco.get("motivo", ""),
            "Corriente de falla máxima tabulada (kA)": arco.get("corriente_maxima"),
            "Tiempo máximo tabulado (s)": arco.get("tiempo_maximo"),
            "Distancia mínima tabulada (mm)": arco.get("distancia_minima"),

            "Aproximación limitada": limitada,

            "Aproximación restringida": restringida,

            "Clase de guante": (
                guante if guante is not None
                else "No determinada"
            ),

            "Referencia arco": (
                "130.7(C)(15)(a)"
                if sistema == "CA"
                else "130.7(C)(15)(b)"
            ),

            "Referencia choque": (
                "130.4(E)(a)"
                if sistema == "CA"
                else "130.4(E)(b)"
            ),

            "Estado documental": (
                "Pendiente de revisión técnica"
            )
        }

        st.session_state[
            f"{clave}_resultado"
        ] = detalle

    detalle = st.session_state.get(
        f"{clave}_resultado"
    )

    if detalle:
        presentar_resultado(detalle)

        st.caption(
            "Los resultados corresponden a los "
            "últimos datos evaluados. Si modifica "
            "los parámetros, evalúe nuevamente."
        )

        if st.button(
            (
                "Guardar nueva revisión"
                if registro
                else "Guardar evaluación"
            ),
            type="primary",
            key=f"{clave}_guardar"
        ):
            try:
                if registro:
                    guardado = actualizar(
                        "arco_electrico",
                        registro["id"],
                        {"detalle": detalle}
                    )

                else:
                    guardado = insertar(
                        "arco_electrico",
                        {
                            "proyecto_id": proyecto["id"],
                            "detalle": detalle
                        }
                    )

                if guardado:
                    st.session_state.pop(
                        f"{clave}_resultado",
                        None
                    )

                    notificar(
                        "arco",
                        "Evaluación guardada correctamente."
                    )

            except Exception as error:
                st.error(
                    f"No se pudo guardar: {error}"
                )


def detalle_consultable(detalle):
    if detalle.get("Versión de criterios de arco") != REVISION_CRITERIOS:
        detalle = {
            **detalle,
            "Aproximación limitada": "Pendiente de reevaluación",
            "Aproximación restringida": "Pendiente de reevaluación",
            "Clase de guante": "Pendiente de reevaluación"
        }
    if detalle.get("Método aplicable") == "Sí" and not resultado_arco_vigente(detalle):
        return {
            **detalle, "Método aplicable": "Pendiente de reevaluación", "Categoría": None,
            "Frontera de arco": None, "Protección mínima": None,
            "Motivo": "Reevalúe el punto con los criterios actuales."
        }
    return detalle


def consultar_evaluaciones(proyecto):
    registros = consultar(
        "arco_electrico",
        {"proyecto_id": proyecto["id"]}
    )

    if not registros:
        st.info(
            "No hay evaluaciones registradas."
        )

        return

    detalles = [
        detalle_consultable(r.get("detalle") or {})
        for r in registros
    ]

    tabla = pd.DataFrame(detalles)

    st.dataframe(
        tabla.reindex(columns=[
            "Código del punto",
            "Equipo",
            "Ubicación",
            "Sistema",
            "Tensión (V)",
            "Método aplicable",
            "Categoría",
            "Revisión"
        ]),
        hide_index=True,
        use_container_width=True
    )

    opciones = {
        r["id"]: r
        for r in registros
    }

    seleccionado = st.selectbox(
        "Seleccionar punto de análisis",
        list(opciones),
        format_func=lambda x: (
            str(
                opciones[x]["detalle"].get(
                    "Equipo", "Sin nombre"
                )
            )
            + " | "
            + str(
                opciones[x]["detalle"].get(
                    "Código del punto",
                    str(x)[:8]
                )
            )
        ),
        key=f"arco_consulta_{proyecto['id']}"
    )

    registro = opciones[seleccionado]

    detalle = detalle_consultable(registro.get("detalle") or {})

    c1, c2 = st.columns(2)

    c1.markdown(f"**Código:** {detalle.get('Código del punto') or str(seleccionado)[:8]}")
    c2.markdown(f"**Revisión:** {detalle.get('Revisión') or 1}")

    presentar_resultado(detalle)

    with st.expander(
        "Datos técnicos completos"
    ):
        st.dataframe(
            pd.DataFrame([
                {
                    "Campo": campo,
                    "Valor": str(valor)
                }
                for campo, valor in detalle.items()
            ]),
            hide_index=True,
            use_container_width=True
        )

    with st.expander(
        "Editar evaluación"
    ):
        formulario_evaluacion(
            proyecto,
            registro
        )

    pdf = generar_pdf(
        "Evaluación de arco y choque eléctrico",
        proyecto,
        [
            ("Resultados técnicos", detalle)
        ],
        (
            "Referencia académica: NFPA 70E 2027. "
            "Resultados sujetos a validación."
        )
    )

    st.download_button(
        "Descargar informe PDF",
        pdf,
        file_name=(
            "evaluacion_"
            + str(seleccionado)[:8]
            + ".pdf"
        ),
        mime="application/pdf",
        key=f"arco_pdf_{seleccionado}",
        type="primary",
        on_click="ignore",
    )

    with st.expander(
        "Eliminar evaluación"
    ):
        st.warning(
            "La eliminación puede afectar "
            "la trazabilidad de documentos "
            "asociados al punto."
        )

        confirmar = st.checkbox(
            "Confirmo la eliminación",
            key=f"arco_confirmar_{seleccionado}"
        )

        if st.button(
            "Eliminar evaluación",
            disabled=not confirmar,
            key=f"arco_eliminar_{seleccionado}"
        ):
            try:
                if eliminar(
                    "arco_electrico",
                    seleccionado
                ):
                    notificar(
                        "arco",
                        "Evaluación eliminada."
                    )

            except Exception as error:
                st.error(str(error))


def seleccionar_epp(proyecto):
    registros = consultar(
        "arco_electrico",
        {"proyecto_id": proyecto["id"]}
    )

    validos = {}

    for registro in registros:
        detalle = registro.get("detalle") or {}

        try:
            categoria = int(
                detalle.get("Categoría")
            )

        except (TypeError, ValueError):
            continue

        if (
            resultado_arco_vigente(detalle)
            and categoria in PROTECCION_ARCO
        ):
            validos[registro["id"]] = registro

    if not validos:
        st.info(
            "No existen evaluaciones guardadas "
            "con una categoría asignada."
        )

        with st.expander(
            "Consultar guía general"
        ):
            mostrar_guia_epp(
                clave=f"guia_{proyecto['id']}"
            )

        return

    seleccionado = st.selectbox(
        "Punto de análisis",
        list(validos),
        format_func=lambda x: (
            str(
                validos[x]["detalle"].get(
                    "Equipo", ""
                )
            )
            + " | Categoría "
            + str(
                validos[x]["detalle"].get(
                    "Categoría"
                )
            )
        ),
        key=f"epp_punto_{proyecto['id']}"
    )

    detalle = validos[seleccionado]["detalle"]

    presentar_resultado(detalle)

    seleccion = mostrar_guia_epp(
        categoria=int(detalle["Categoría"]),
        clave=(
            f"epp_{seleccionado}_"
            f"{detalle.get('Revisión')}"
        ),
        anterior=detalle.get(
            "Selección EPP", {}
        )
    )

    if st.button(
        "Guardar selección de EPP",
        key=f"guardar_epp_{seleccionado}"
    ):
        actualizado = dict(
            detalle,
            **{"Selección EPP": seleccion}
        )

        actualizar(
            "arco_electrico",
            seleccionado,
            {"detalle": actualizado}
        )

        st.toast(
            "Selección de EPP guardada."
        )

        st.rerun()


def mostrar():
    st.title(
        "04. Arco eléctrico, EPP y fronteras"
    )

    advertencia_tecnica()

    mostrar_aviso("arco")

    proyecto = seleccionar_proyecto("arco")

    if not proyecto:
        return

    tab1, tab2, tab3 = st.tabs([
        "Nueva evaluación",
        "Consultar y editar",
        "Selección de EPP"
    ])

    with tab1:
        formulario_evaluacion(proyecto)

    with tab2:
        consultar_evaluaciones(proyecto)

    with tab3:
        seleccionar_epp(proyecto)
