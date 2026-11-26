
import streamlit as st
import pandas as pd

from database import consultar, insertar, eliminar

from modules.comunes import (
    seleccionar_proyecto,
    mostrar_aviso,
    notificar,
    advertencia_tecnica
)

from modules.tablas_nfpa import (
    TABLA_CA,
    calcular_arco,
    limites_choque,
    clase_guante,
    PROTECCION_ARCO
)

from modules.reportes import generar_pdf


def distancia_texto(valor):

    if valor is None:
        return "No especificado"

    if isinstance(valor, str):
        return valor

    return f"{valor} m"


def presentar_resultado(detalle):

    st.subheader("Resultados de protección contra arco")

    if detalle["Método aplicable"] == "Sí":

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Categoría de EPP",
            detalle["Categoría"]
        )

        c2.metric(
            "Protección mínima",
            f"{detalle['Protección mínima']} cal/cm²"
        )

        c3.metric(
            "Frontera de arco",
            f"{detalle['Frontera de arco']} m"
        )

        st.success(
            "Los parámetros ingresados coinciden "
            "con una fila implementada de la tabla."
        )

    else:

        st.error(detalle["Motivo"])

    st.subheader("Protección contra choque eléctrico")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Aproximación limitada",
        detalle["Aproximación limitada"]
    )

    c2.metric(
        "Aproximación restringida",
        detalle["Aproximación restringida"]
    )

    c3.metric(
        "Clase orientativa de guante",
        detalle["Clase de guante"]
    )

    st.caption(
        "La clase de guante se determina únicamente "
        "por tensión. No sustituye la selección completa "
        "de protección contra choque."
    )

    st.warning(
        "La selección final de EPP, las notas de las "
        "tablas y las condiciones del equipo deben ser "
        "verificadas por una persona calificada."
    )


def mostrar():

    st.title("04. Arco eléctrico, EPP y fronteras")

    advertencia_tecnica()
    mostrar_aviso("arco")

    proyecto = seleccionar_proyecto("arco")

    if not proyecto:
        return

    pestana1, pestana2 = st.tabs([
        "Nueva evaluación",
        "Consultar evaluaciones"
    ])

    with pestana1:

        sistema = st.radio(
            "Tipo de sistema",
            ["CA", "CC"],
            horizontal=True
        )

        equipos = (
            list(TABLA_CA)
            if sistema == "CA"
            else ["Baterías y equipos de CC"]
        )

        with st.form("formulario_arco"):

            nombre = st.text_input(
                "Identificación del equipo *"
            )

            equipo = st.selectbox(
                "Tipo y clasificación del equipo",
                equipos
            )

            tarea = st.text_area(
                "Tarea que se realizará *"
            )

            ubicacion = st.text_input("Ubicación del equipo")

            c1, c2 = st.columns(2)

            voltaje = c1.number_input(
                "Tensión nominal (V)",
                min_value=0,
                value=0
            )

            corriente = c2.number_input(
                "Corriente de falla disponible (kA)",
                min_value=0.0,
                value=0.0,
                format="%.3f"
            )

            tiempo = c1.number_input(
                "Tiempo de despeje o duración del arco (s)",
                min_value=0.0,
                value=0.0,
                format="%.4f"
            )

            distancia = c2.number_input(
                "Distancia de trabajo (mm)",
                min_value=0,
                value=0
            )

            altitud = st.number_input(
                "Elevación del sitio (m s. n. m.)",
                min_value=0,
                value=0
            )

            movil = st.radio(
                "Tipo de parte energizada expuesta",
                ["Parte fija", "Conductor móvil"]
            )

            fuente = st.text_area(
                "Fuente de los datos eléctricos *",
                placeholder=(
                    "Estudio de cortocircuito, "
                    "curvas de protección, planos, etc."
                )
            )

            requiere_epp = st.checkbox(
                "La evaluación previa de arco indica "
                "que se requiere EPP contra arco eléctrico"
            )

            condiciones = st.checkbox(
                "Se verificó la clasificación del equipo, "
                "su mantenimiento y las notas aplicables "
                "de la tabla normativa"
            )

            solo_tablas = st.checkbox(
                "Se utilizará el método de categorías, "
                "sin combinarlo con energía incidente"
            )

            evaluar = st.form_submit_button(
                "Evaluar parámetros",
                type="primary",
                use_container_width=True
            )

        if evaluar:

            if not all([
                nombre.strip(),
                tarea.strip(),
                fuente.strip()
            ]) or min(
                voltaje, corriente, tiempo, distancia
            ) <= 0:

                st.error(
                    "Completa la identificación y todos "
                    "los parámetros técnicos obligatorios."
                )

            else:

                arco = calcular_arco(
                    sistema,
                    equipo,
                    voltaje,
                    corriente,
                    tiempo,
                    distancia
                )

                if not all([
                    requiere_epp,
                    condiciones,
                    solo_tablas
                ]):

                    arco = {
                        "aplicable": False,
                        "motivo": (
                            "Falta verificar las condiciones "
                            "previas de aplicación del método."
                        )
                    }

                choque = limites_choque(
                    sistema,
                    voltaje,
                    movil == "Conductor móvil"
                )

                limitada = (
                    distancia_texto(choque["limitada"])
                    if choque else "Fuera de alcance"
                )

                restringida = (
                    distancia_texto(choque["restringida"])
                    if choque else "Fuera de alcance"
                )

                if altitud > 900:

                    restringida = (
                        "Requiere revisión por altitud"
                    )

                guante = clase_guante(sistema, voltaje)

                detalle = {
                    "Equipo": nombre,
                    "Tipo de equipo": equipo,
                    "Ubicación": ubicacion,
                    "Tarea": tarea,
                    "Sistema": sistema,
                    "Tensión (V)": voltaje,
                    "Corriente de falla (kA)": corriente,
                    "Tiempo (s)": tiempo,
                    "Distancia de trabajo (mm)": distancia,
                    "Altitud (m)": altitud,
                    "Parte expuesta": movil,
                    "Fuente de datos": fuente,
                    "Método aplicable": (
                        "Sí" if arco["aplicable"] else "No"
                    ),
                    "Categoría": arco.get("categoria"),
                    "Frontera de arco": arco.get("frontera"),
                    "Protección mínima": PROTECCION_ARCO.get(
                        arco.get("categoria")
                    ),
                    "Motivo": arco.get("motivo", ""),
                    "Aproximación limitada": limitada,
                    "Aproximación restringida": restringida,
                    "Clase de guante": (
                        guante if guante is not None
                        else "Fuera de alcance"
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
                    )
                }

                st.session_state.resultado_arco = {
                    "proyecto_id": proyecto["id"],
                    "detalle": detalle
                }

        resultado = st.session_state.get("resultado_arco")

        if (
            resultado
            and resultado["proyecto_id"] == proyecto["id"]
        ):

            detalle = resultado["detalle"]

            presentar_resultado(detalle)

            st.caption(
                "Los resultados corresponden a los últimos "
                "datos evaluados, no a cambios sin evaluar."
            )

            if st.button(
                "Guardar evaluación",
                type="primary"
            ):

                try:

                    existentes = consultar(
                        "arco_electrico",
                        {"proyecto_id": proyecto["id"]}
                    )

                    duplicado = any(
                        r.get("detalle") == detalle
                        for r in existentes
                    )

                    if duplicado:

                        st.warning(
                            "Esta evaluación ya está registrada."
                        )

                    else:

                        guardado = insertar(
                            "arco_electrico",
                            resultado
                        )

                        if guardado:

                            st.session_state.pop(
                                "resultado_arco", None
                            )

                            notificar(
                                "arco",
                                "Evaluación registrada exitosamente."
                            )

                except Exception as error:

                    st.error(str(error))

    with pestana2:

        registros = consultar(
            "arco_electrico",
            {"proyecto_id": proyecto["id"]}
        )

        if not registros:

            st.info("No hay evaluaciones registradas.")
            return

        detalles = [
            r.get("detalle") or {}
            for r in registros
        ]

        tabla = pd.DataFrame(detalles)

        st.dataframe(
            tabla.reindex(columns=[
                "Equipo",
                "Sistema",
                "Tensión (V)",
                "Método aplicable",
                "Categoría",
                "Frontera de arco"
            ]),
            hide_index=True,
            use_container_width=True
        )

        opciones = {r["id"]: r for r in registros}

        seleccionado = st.selectbox(
            "Seleccionar evaluación",
            list(opciones),
            format_func=lambda x: (
                opciones[x].get("detalle", {}).get(
                    "Equipo", "Sin nombre"
                )
                + " | " + str(x)[:8]
            )
        )

        detalle = opciones[seleccionado]["detalle"]

        presentar_resultado(detalle)

        with st.expander("Datos técnicos completos"):

            for campo, valor in detalle.items():

                st.write(f"**{campo}:** {valor}")

        pdf = generar_pdf(
            "Evaluación de arco y choque eléctrico",
            proyecto,
            [("Resultados técnicos", detalle)],
            "NFPA 70E 2027: 130.4(E), 130.5, "
            "130.7(C)(7)(a) y 130.7(C)(15)."
        )

        st.download_button(
            "Descargar informe PDF",
            pdf,
            "evaluacion_arco_electrico.pdf",
            "application/pdf",
            type="primary"
        )

        with st.expander("Eliminar evaluación"):

            confirmar = st.checkbox(
                "Confirmo la eliminación de esta evaluación"
            )

            if st.button(
                "Eliminar evaluación",
                disabled=not confirmar
            ):

                if eliminar("arco_electrico", seleccionado):

                    notificar(
                        "arco",
                        "Evaluación eliminada correctamente."
                    )
