
import streamlit as st
import pandas as pd

from database import consultar, insertar, actualizar, eliminar
from modules.comunes import notificar, mostrar_aviso
from modules.reportes import generar_pdf


def administrar_documentos(
    tabla,
    proyecto,
    titulo,
    campos,
    referencia,
    inicial=None,
    tipo=None
):

    mostrar_aviso(tabla)

    registros = consultar(
        tabla,
        {"proyecto_id": proyecto["id"]}
    )

    if tipo:
        registros = [
            r for r in registros
            if (r.get("detalle") or {}).get("Tipo") == tipo
        ]

    opciones = {
        r["id"]: r for r in registros
    }

    accion = st.radio(
        "Acción",
        ["Crear documento", "Consultar y editar"],
        horizontal=True,
        key=f"accion_{tabla}_{tipo}"
    )

    registro = {}

    if accion == "Consultar y editar":

        if not registros:
            st.info("No hay documentos registrados.")
            return

        seleccion = st.selectbox(
            "Seleccionar documento",
            list(opciones),
            format_func=lambda x: (
                opciones[x].get("detalle", {}).get(
                    "Identificación", "Documento"
                ) + " | " + str(x)[:8]
            ),
            key=f"seleccion_{tabla}_{tipo}"
        )

        registro = opciones[seleccion]

    anterior = (
        registro.get("detalle")
        or inicial
        or {}
    )

    clave = f"{tabla}_{tipo}_{registro.get('id', 'nuevo')}"

    with st.form("form_" + clave):

        detalle = {}

        for seccion, lista_campos in campos.items():

            st.subheader(seccion)

            for campo in lista_campos:

                detalle[campo] = st.text_area(
                    campo,
                    value=str(anterior.get(campo) or ""),
                    height=85
                )

        guardar = st.form_submit_button(
            "Guardar documento",
            type="primary",
            use_container_width=True
        )

    if guardar:

        if not detalle.get("Identificación", "").strip():

            st.error("Completa la identificación.")
            return

        if tipo:
            detalle["Tipo"] = tipo

        detalle["Estado"] = "Borrador académico"

        datos = {
            "proyecto_id": proyecto["id"],
            "detalle": detalle
        }

        try:

            if registro:

                respuesta = actualizar(
                    tabla,
                    registro["id"],
                    datos
                )

            else:

                duplicado = any(
                    (r.get("detalle") or {}).get(
                        "Identificación", ""
                    ).strip().lower()
                    == detalle["Identificación"].strip().lower()
                    for r in registros
                )

                if duplicado:
                    st.warning(
                        "Ya existe un documento "
                        "con esta identificación."
                    )
                    return

                respuesta = insertar(tabla, datos)

            if respuesta:

                notificar(
                    tabla,
                    "Documento guardado exitosamente."
                )

            else:
                st.error("No se confirmó el guardado.")

        except Exception as error:
            st.error(str(error))

    if registro:

        guardado = registro.get("detalle") or {}

        secciones = []

        for seccion, lista_campos in campos.items():

            secciones.append((
                seccion,
                {
                    campo: guardado.get(campo)
                    for campo in lista_campos
                }
            ))

        pdf = generar_pdf(
            titulo + " - BORRADOR",
            proyecto,
            secciones,
            referencia
        )

        st.download_button(
            "Descargar documento PDF",
            pdf,
            f"{tabla}.pdf",
            "application/pdf",
            key=f"pdf_{clave}"
        )

        with st.expander("Eliminar documento"):

            confirmar = st.checkbox(
                "Confirmo la eliminación",
                key=f"confirmar_{clave}"
            )

            if st.button(
                "Eliminar",
                disabled=not confirmar,
                key=f"eliminar_{clave}"
            ):

                if eliminar(tabla, registro["id"]):

                    notificar(
                        tabla,
                        "Documento eliminado correctamente."
                    )
