
import streamlit as st
import pandas as pd

from datetime import datetime, timezone

from database import consultar, insertar, actualizar, eliminar
from modules.comunes import notificar, mostrar_aviso
from modules.reportes import generar_pdf


def fecha_actual():

    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )


def normalizar(valor):

    return " ".join(str(valor or "").split()).casefold()


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

    prefijo = f"{tabla}_{tipo}_{proyecto['id']}"

    registros = consultar(
        tabla,
        {"proyecto_id": proyecto["id"]}
    )

    if tipo:

        registros = [
            r for r in registros
            if (r.get("detalle") or {}).get("Tipo") == tipo
        ]

    accion = st.radio(
        "Acción",
        ["Crear documento", "Consultar y editar"],
        horizontal=True,
        key=f"accion_{prefijo}"
    )

    registro = {}

    if accion == "Consultar y editar":

        if not registros:

            st.info("No hay documentos registrados.")
            return

        c1, c2 = st.columns(2)

        with c1:

            buscar = st.text_input(
                "Buscar documento",
                key=f"buscar_{prefijo}"
            )

        with c2:

            filtro = st.selectbox(
                "Filtrar por estado",
                [
                    "Todos",
                    "Borrador",
                    "Pendiente de revisión",
                    "Revisado",
                    "Aprobado",
                    "Rechazado"
                ],
                key=f"filtro_{prefijo}"
            )

        filtrados = []

        for r in registros:

            d = r.get("detalle") or {}

            estado = d.get("Estado", "Borrador")

            if estado == "Borrador académico":
                estado = "Borrador"

            texto = " ".join([
                str(d.get("Identificación", "")),
                str(d.get("Equipo", "")),
                str(d.get("Ubicación", ""))
            ])

            if normalizar(buscar) not in normalizar(texto):
                continue

            if filtro != "Todos" and estado != filtro:
                continue

            filtrados.append(r)

        if not filtrados:

            st.info("No hay documentos que coincidan.")
            return

        resumen = []

        for r in filtrados:

            d = r.get("detalle") or {}

            resumen.append({
                "Identificación": d.get("Identificación"),
                "Equipo": d.get("Equipo"),
                "Estado": d.get("Estado", "Borrador"),
                "Última modificación": d.get(
                    "Última modificación", ""
                )
            })

        st.dataframe(
            pd.DataFrame(resumen),
            hide_index=True,
            use_container_width=True
        )

        opciones = {
            r["id"]: r for r in filtrados
        }

        seleccion = st.selectbox(
            "Seleccionar documento",
            list(opciones),
            format_func=lambda x: (
                str(opciones[x].get("detalle", {}).get(
                    "Identificación", "Documento"
                ))
                + " | "
                + str(opciones[x].get("detalle", {}).get(
                    "Estado", "Borrador"
                ))
            ),
            key=f"seleccion_{prefijo}"
        )

        registro = opciones[seleccion]

    anterior = registro.get("detalle") or inicial or {}

    estado = anterior.get("Estado", "Borrador")

    if estado == "Borrador académico":
        estado = "Borrador"

    historial = anterior.get("Historial") or []

    clave = (
        f"{prefijo}_{registro.get('id', 'nuevo')}_"
        f"{len(historial)}"
    )

    editable = (
        not registro
        or estado in ["Borrador", "Rechazado"]
    )

    if registro:

        st.subheader("Estado del documento")

        if estado == "Aprobado":

            st.success("Aprobado documentalmente")

        elif estado == "Rechazado":

            st.error("Rechazado: requiere correcciones")

        elif estado == "Pendiente de revisión":

            st.warning("Pendiente de revisión")

        elif estado == "Revisado":

            st.info("Revisado: pendiente de aprobación")

        else:

            st.info("Borrador")

    if not editable:

        st.caption(
            "El documento está protegido contra edición. "
            "Debe regresar a borrador para modificarlo."
        )

    with st.form("form_" + clave):

        detalle = {}

        for seccion, lista_campos in campos.items():

            with st.expander(seccion, expanded=True):

                for campo in lista_campos:

                    detalle[campo] = st.text_area(
                        campo,
                        value=str(anterior.get(campo) or ""),
                        height=85,
                        disabled=not editable,
                        key=f"{clave}_{seccion}_{campo}"
                    )

        guardar = st.form_submit_button(
            "Guardar documento",
            type="primary",
            disabled=not editable,
            use_container_width=True
        )

    if guardar:

        identificacion = detalle.get(
            "Identificación", ""
        ).strip()

        if not identificacion:

            st.error("Completa la identificación.")
            return

        duplicado = any(
            r["id"] != registro.get("id")
            and normalizar(
                (r.get("detalle") or {}).get(
                    "Identificación", ""
                )
            ) == normalizar(identificacion)
            for r in registros
        )

        if duplicado:

            st.warning(
                "Ya existe un documento con esta identificación."
            )
            return

        detalle["Identificación"] = identificacion

        if tipo:
            detalle["Tipo"] = tipo

        detalle["Estado"] = "Borrador"

        detalle["Creado por"] = anterior.get(
            "Creado por",
            str(st.session_state.get("usuario", "Usuario"))
        )

        detalle["Fecha de creación"] = anterior.get(
            "Fecha de creación",
            fecha_actual()
        )

        detalle["Última modificación"] = fecha_actual()

        detalle["Historial"] = historial + [{
            "Acción": (
                "Documento editado"
                if registro
                else "Documento creado"
            ),
            "Estado": "Borrador",
            "Responsable": str(
                st.session_state.get("usuario", "Usuario")
            ),
            "Fecha": fecha_actual(),
            "Observaciones": "Guardado de información"
        }]

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

                respuesta = insertar(tabla, datos)

            if respuesta:

                notificar(
                    tabla,
                    "Documento guardado exitosamente."
                )

            else:

                st.error("No se confirmó el guardado.")

        except Exception as error:

            st.error(f"No se pudo guardar: {error}")

    if not registro:
        return

    guardado = registro.get("detalle") or {}

    st.divider()

    st.subheader("Revisión y aprobación documental")

    transiciones = {
        "Borrador": [
            ("Enviar a revisión", "Pendiente de revisión")
        ],
        "Pendiente de revisión": [
            ("Registrar revisión", "Revisado"),
            ("Rechazar documento", "Rechazado"),
            ("Devolver a borrador", "Borrador")
        ],
        "Revisado": [
            ("Aprobar documento", "Aprobado"),
            ("Rechazar documento", "Rechazado"),
            ("Devolver a borrador", "Borrador")
        ],
        "Aprobado": [
            ("Reabrir para modificación", "Borrador")
        ],
        "Rechazado": [
            ("Regresar a borrador", "Borrador")
        ]
    }

    opciones_estado = dict(
        transiciones.get(estado, [])
    )

    if opciones_estado:

        with st.form(f"revision_{clave}"):

            movimiento = st.selectbox(
                "Acción documental",
                list(opciones_estado)
            )

            responsable = st.text_input(
                "Nombre y apellidos del responsable"
            )

            cargo = st.text_input(
                "Cargo o función"
            )

            observaciones = st.text_area(
                "Observaciones y fundamento"
            )

            confirmar = st.checkbox(
                "Confirmo el registro de esta acción "
                "para fines académicos."
            )

            aplicar = st.form_submit_button(
                "Registrar acción",
                type="primary"
            )

        if aplicar:

            nuevo_estado = opciones_estado[movimiento]

            faltantes = [
                campo
                for lista in campos.values()
                for campo in lista
                if not str(guardado.get(campo) or "").strip()
            ]

            if not all([
                responsable.strip(),
                cargo.strip(),
                observaciones.strip(),
                confirmar
            ]):

                st.error(
                    "Completa los datos del responsable, "
                    "las observaciones y la confirmación."
                )

            elif nuevo_estado in [
                "Pendiente de revisión",
                "Revisado",
                "Aprobado"
            ] and faltantes:

                st.error(
                    "Completa los campos del documento antes "
                    "de continuar. Si alguno no aplica, "
                    "documenta el motivo."
                )

                st.write(faltantes)

            else:

                nuevo = dict(guardado)

                nuevo["Estado"] = nuevo_estado

                nuevo["Última modificación"] = fecha_actual()

                nuevo["Historial"] = historial + [{
                    "Acción": movimiento,
                    "Estado": nuevo_estado,
                    "Responsable": responsable.strip(),
                    "Cargo": cargo.strip(),
                    "Usuario registrado": str(
                        st.session_state.get("usuario", "")
                    ),
                    "Fecha": fecha_actual(),
                    "Observaciones": observaciones.strip()
                }]

                try:

                    respuesta = actualizar(
                        tabla,
                        registro["id"],
                        {
                            "proyecto_id": proyecto["id"],
                            "detalle": nuevo
                        }
                    )

                    if respuesta:

                        notificar(
                            tabla,
                            f"Estado actualizado: {nuevo_estado}."
                        )

                    else:

                        st.error(
                            "No se confirmó la actualización."
                        )

                except Exception as error:

                    st.error(str(error))

    st.divider()

    st.subheader("Historial documental")

    if historial:

        st.dataframe(
            pd.DataFrame(historial),
            hide_index=True,
            use_container_width=True
        )

    else:

        st.info("No hay movimientos registrados.")

    secciones = []

    for seccion, lista_campos in campos.items():

        secciones.append((
            seccion,
            {
                campo: guardado.get(campo, "")
                for campo in lista_campos
            }
        ))

    secciones.append((
        "Control documental",
        {
            "Estado": estado,
            "Creado por": guardado.get("Creado por", ""),
            "Fecha de creación": guardado.get(
                "Fecha de creación", ""
            ),
            "Última modificación": guardado.get(
                "Última modificación", ""
            ),
            "Validez": (
                "Documento académico. No constituye "
                "autorización de trabajo eléctrico."
            )
        }
    ))

    for i, movimiento in enumerate(historial, 1):

        secciones.append((
            f"Registro de revisión {i}",
            movimiento
        ))

    pdf = generar_pdf(
        titulo + " - " + estado.upper(),
        proyecto,
        secciones,
        referencia
    )

    st.download_button(
        "Descargar documento PDF",
        pdf,
        f"{tabla}_{registro['id']}.pdf",
        "application/pdf",
        key=f"pdf_{clave}",
        use_container_width=True
    )

    if estado in ["Borrador", "Rechazado"]:

        with st.expander("Eliminar documento"):

            confirmar_eliminar = st.checkbox(
                "Confirmo la eliminación permanente",
                key=f"confirmar_{clave}"
            )

            if st.button(
                "Eliminar documento",
                disabled=not confirmar_eliminar,
                key=f"eliminar_{clave}"
            ):

                try:

                    if eliminar(tabla, registro["id"]):

                        notificar(
                            tabla,
                            "Documento eliminado correctamente."
                        )

                    else:

                        st.error("No se confirmó la eliminación.")

                except Exception as error:

                    st.error(str(error))
