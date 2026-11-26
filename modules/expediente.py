
import streamlit as st
import pandas as pd

from database import consultar
from modules.comunes import seleccionar_proyecto
from modules.reportes import generar_pdf


SECCIONES = {
    "evaluaciones": "Evaluaciones de riesgos",
    "riesgos": "Registros de peligros",
    "arco_electrico": "Evaluaciones de arco eléctrico",
    "etiquetas": "Etiquetas eléctricas",
    "loto": "Documentación LOTO",
    "permisos": "Permisos de trabajo"
}


def preparar_detalle(registro):

    detalle = registro.get("detalle")

    if isinstance(detalle, dict):

        return detalle

    return {
        campo: valor
        for campo, valor in registro.items()
        if campo not in [
            "id",
            "proyecto_id",
            "fecha_creacion"
        ]
    }


def mostrar():

    st.title("Expediente del proyecto")

    st.caption(
        "Consulta consolidada de los registros "
        "y documentos técnicos."
    )

    proyecto = seleccionar_proyecto("expediente")

    if not proyecto:
        return

    datos = {}

    try:

        for tabla, nombre in SECCIONES.items():

            datos[tabla] = consultar(
                tabla,
                {"proyecto_id": proyecto["id"]}
            )

    except Exception:

        st.error(
            "No se pudo recuperar el expediente completo."
        )

        return

    st.subheader("Resumen documental")

    columnas = st.columns(3)

    for i, (tabla, nombre) in enumerate(
        SECCIONES.items()
    ):

        columnas[i % 3].metric(
            nombre,
            len(datos[tabla])
        )

    st.divider()

    st.subheader("Información del proyecto")

    st.write(
        "**Nombre:**",
        proyecto.get("nombre")
    )

    st.write(
        "**Código:**",
        proyecto.get("codigo")
    )

    st.write(
        "**Descripción:**",
        proyecto.get("descripcion")
    )

    st.subheader("Consultar registros")

    seleccion = st.selectbox(
        "Tipo de documentación",
        list(SECCIONES),
        format_func=lambda x: SECCIONES[x]
    )

    registros = datos[seleccion]

    if registros:

        detalles = [
            preparar_detalle(r)
            for r in registros
        ]

        st.dataframe(
            pd.DataFrame(detalles),
            hide_index=True,
            use_container_width=True
        )

    else:

        st.info(
            "No existen registros de este tipo."
        )

    st.divider()

    st.subheader("Exportar expediente")

    incluir = st.multiselect(
        "Información que desea incluir",
        list(SECCIONES),
        default=list(SECCIONES),
        format_func=lambda x: SECCIONES[x]
    )

    if incluir:

        secciones = [
            (
                "Información general",
                {
                    "Proyecto": proyecto.get("nombre"),
                    "Código": proyecto.get("codigo"),
                    "Descripción": proyecto.get("descripcion"),
                    "Estado": "Expediente académico"
                }
            )
        ]

        for tabla in incluir:

            if not datos[tabla]:

                secciones.append((
                    SECCIONES[tabla],
                    {
                        "Estado": "Sin registros"
                    }
                ))

            for i, registro in enumerate(
                datos[tabla], start=1
            ):

                secciones.append((
                    f"{SECCIONES[tabla]} - Registro {i}",
                    preparar_detalle(registro)
                ))

        if st.button(
            "Preparar expediente PDF",
            type="primary"
        ):

            try:

                pdf = generar_pdf(
                    "Expediente de seguridad eléctrica",
                    proyecto,
                    secciones,
                    "NFPA 70E, edición 2027. "
                    "Documentación académica."
                )

                st.download_button(
                    "Descargar expediente",
                    pdf,
                    file_name="expediente_electrico.pdf",
                    mime="application/pdf"
                )

            except Exception:

                st.error(
                    "No se pudo generar el expediente."
                )
