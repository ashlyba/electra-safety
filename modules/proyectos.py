
import streamlit as st
import pandas as pd

from datetime import date
from database import consultar, insertar, actualizar, eliminar


ESTADOS = [
    "En planificación",
    "En ejecución",
    "Finalizado",
    "Suspendido"
]


def proyecto_duplicado(cliente_id, nombre, excluir=None):

    existentes = consultar(
        "proyectos",
        {"cliente_id": cliente_id}
    )

    return any(
        p["id"] != excluir
        and p["nombre"].strip().casefold()
        == nombre.strip().casefold()
        for p in existentes
    )


def notificar(mensaje):

    st.session_state.aviso_proyecto = mensaje
    st.session_state.proyecto_guardado = True

    st.rerun()


def formulario_proyecto(clientes, proyecto=None):

    proyecto = proyecto or {}

    identificador = proyecto.get("id", "nuevo")

    opciones = {
        c["id"]: c["nombre_empresa"]
        for c in clientes
    }

    ids = list(opciones)

    indice = 0

    if proyecto.get("cliente_id") in ids:

        indice = ids.index(proyecto["cliente_id"])

    with st.form(f"formulario_proyecto_{identificador}"):

        cliente_id = st.selectbox(
            "Cliente *",
            ids,
            index=indice,
            format_func=lambda x: opciones[x]
        )

        nombre = st.text_input(
            "Nombre del proyecto *",
            value=proyecto.get("nombre") or ""
        )

        descripcion = st.text_area(
            "Descripción y alcance",
            value=proyecto.get("descripcion") or ""
        )

        c1, c2 = st.columns(2)

        with c1:

            ubicacion = st.text_input(
                "Ubicación",
                value=proyecto.get("ubicacion") or ""
            )

            responsable = st.text_input(
                "Profesional responsable",
                value=proyecto.get("responsable") or ""
            )

        with c2:

            inicio = st.date_input(
                "Fecha de inicio",
                value=date.fromisoformat(
                    proyecto["fecha_inicio"]
                ) if proyecto.get("fecha_inicio") else date.today(),
                format="DD/MM/YYYY"
            )

            final = st.date_input(
                "Fecha estimada de finalización",
                value=date.fromisoformat(
                    proyecto["fecha_final"]
                ) if proyecto.get("fecha_final") else None,
                format="DD/MM/YYYY"
            )

        estado = st.selectbox(
            "Estado",
            ESTADOS,
            index=ESTADOS.index(
                proyecto.get("estado") or ESTADOS[0]
            )
        )

        observaciones = st.text_area(
            "Observaciones",
            value=proyecto.get("observaciones") or ""
        )

        st.caption("* Campos obligatorios.")

        if proyecto.get("codigo"):

            st.caption(
                "Código permanente: " + proyecto["codigo"]
            )

        guardar = st.form_submit_button(
            "Guardar proyecto",
            type="primary",
            use_container_width=True
        )

        if not guardar:
            return

        if not nombre.strip():

            st.error("Indica el nombre del proyecto.")
            return

        if final and final < inicio:

            st.error(
                "La fecha final no puede ser anterior "
                "a la fecha de inicio."
            )

            return

        datos = {
            "cliente_id": cliente_id,
            "nombre": nombre.strip(),
            "descripcion": descripcion.strip(),
            "ubicacion": ubicacion.strip(),
            "responsable": responsable.strip(),
            "fecha_inicio": inicio.isoformat(),
            "fecha_final": final.isoformat() if final else None,
            "estado": estado,
            "observaciones": observaciones.strip()
        }

        try:

            if proyecto_duplicado(
                cliente_id,
                nombre,
                proyecto.get("id")
            ):

                st.warning(
                    "Ya existe un proyecto con este nombre "
                    "para el cliente seleccionado."
                )

                return

            if proyecto.get("id"):

                resultado = actualizar(
                    "proyectos",
                    proyecto["id"],
                    datos
                )

                mensaje = (
                    f"Proyecto {nombre} actualizado correctamente."
                )

            else:

                resultado = insertar("proyectos", datos)

                mensaje = (
                    f"Proyecto {nombre} registrado exitosamente."
                )

            if not resultado:

                st.error("No se pudo confirmar el guardado.")
                return

            notificar(mensaje)

        except Exception as error:

            if "23505" in str(error):

                st.warning(
                    "Ya existe un proyecto con ese nombre "
                    "para este cliente."
                )

            else:

                st.error(
                    "No fue posible guardar el proyecto."
                )


def mostrar():

    st.title("02. Gestión de proyectos")

    st.write(
        "Creación, seguimiento y administración "
        "de proyectos de seguridad eléctrica."
    )

    if st.session_state.pop("proyecto_guardado", False):

        st.session_state["accion_proyectos"] = (
            "Consultar proyectos"
        )

        st.session_state["administrar_proyecto"] = (
            "Ver información"
        )

    if "aviso_proyecto" in st.session_state:

        mensaje = st.session_state.pop("aviso_proyecto")

        st.success(mensaje)
        st.toast(mensaje, icon="✅")

    clientes = consultar("clientes")
    proyectos = consultar("proyectos")

    if not clientes:

        st.warning(
            "Debes registrar al menos un cliente "
            "antes de crear un proyecto."
        )

        return

    c1, c2, c3 = st.columns(3)

    c1.metric("Total de proyectos", len(proyectos))

    c2.metric(
        "En ejecución",
        sum(p["estado"] == "En ejecución" for p in proyectos)
    )

    c3.metric(
        "Finalizados",
        sum(p["estado"] == "Finalizado" for p in proyectos)
    )

    opcion = st.radio(
        "Selecciona una acción",
        ["Consultar proyectos", "Nuevo proyecto"],
        horizontal=True,
        key="accion_proyectos"
    )

    st.divider()

    if opcion == "Nuevo proyecto":

        formulario_proyecto(clientes)
        return

    if not proyectos:

        st.info("Todavía no hay proyectos registrados.")
        return

    nombres_clientes = {
        c["id"]: c["nombre_empresa"]
        for c in clientes
    }

    busqueda = st.text_input(
        "Buscar proyecto",
        placeholder="Nombre, código o cliente"
    )

    filtro_estado = st.selectbox(
        "Filtrar por estado",
        ["Todos"] + ESTADOS
    )

    filtrados = [
        p for p in proyectos
        if busqueda.strip().casefold() in " ".join([
            p["nombre"],
            p["codigo"],
            nombres_clientes.get(p["cliente_id"], "")
        ]).casefold()
        and (
            filtro_estado == "Todos"
            or p["estado"] == filtro_estado
        )
    ]

    if not filtrados:

        st.warning("No se encontraron proyectos.")
        return

    registros = [
        {
            "Código": p["codigo"],
            "Proyecto": p["nombre"],
            "Cliente": nombres_clientes.get(
                p["cliente_id"], ""
            ),
            "Estado": p["estado"],
            "Inicio": p["fecha_inicio"]
        }
        for p in filtrados
    ]

    tabla = pd.DataFrame(registros)

    st.dataframe(
        tabla,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "Descargar listado de proyectos",
        data=tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="proyectos_electrasafety.csv",
        mime="text/csv"
    )

    st.divider()

    opciones = {p["id"]: p for p in filtrados}

    seleccionado = st.selectbox(
        "Seleccionar proyecto",
        list(opciones),
        format_func=lambda x: (
            opciones[x]["nombre"]
            + " | "
            + opciones[x]["codigo"]
        )
    )

    proyecto = opciones[seleccionado]

    accion = st.radio(
        "Administrar proyecto",
        ["Ver información", "Editar", "Duplicar", "Eliminar"],
        horizontal=True,
        key="administrar_proyecto"
    )

    if accion == "Ver información":

        st.subheader(proyecto["nombre"])

        st.write("**Código:**", proyecto["codigo"])

        st.write(
            "**Cliente:**",
            nombres_clientes.get(proyecto["cliente_id"], "")
        )

        st.write("**Estado:**", proyecto["estado"])

        st.write(
            "**Ubicación:**",
            proyecto.get("ubicacion") or "-"
        )

        st.write(
            "**Responsable:**",
            proyecto.get("responsable") or "-"
        )

        st.write(
            "**Descripción:**",
            proyecto.get("descripcion") or "-"
        )

        st.write(
            "**Fecha de inicio:**",
            proyecto.get("fecha_inicio") or "-"
        )

        st.write(
            "**Fecha final:**",
            proyecto.get("fecha_final") or "-"
        )

        st.write(
            "**Observaciones:**",
            proyecto.get("observaciones") or "-"
        )

        activo = (
            st.session_state.get("proyecto_activo")
            == seleccionado
        )

        if activo:

            st.success("Este es el proyecto activo.")

        if st.button(
            "Establecer como proyecto activo",
            type="primary",
            disabled=activo
        ):

            st.session_state.proyecto_activo = seleccionado

            st.session_state.aviso_proyecto = (
                f"Proyecto {proyecto['nombre']} "
                "seleccionado correctamente."
            )

            st.rerun()

    elif accion == "Editar":

        formulario_proyecto(clientes, proyecto)

    elif accion == "Duplicar":

        st.info(
            "Se creará un proyecto independiente "
            "con un nuevo código y los mismos datos generales."
        )

        nuevo_nombre = st.text_input(
            "Nombre de la copia",
            value=proyecto["nombre"] + " - Copia",
            key=f"copia_{seleccionado}"
        )

        if st.button("Duplicar proyecto"):

            if not nuevo_nombre.strip():

                st.error("Indica el nombre de la copia.")
                return

            try:

                if proyecto_duplicado(
                    proyecto["cliente_id"],
                    nuevo_nombre
                ):

                    st.warning(
                        "Ya existe un proyecto con ese nombre. "
                        "Escribe otro nombre para la copia."
                    )

                    return

                campos = [
                    "cliente_id",
                    "descripcion",
                    "ubicacion",
                    "responsable",
                    "observaciones"
                ]

                datos = {
                    campo: proyecto.get(campo)
                    for campo in campos
                }

                datos["nombre"] = nuevo_nombre.strip()
                datos["estado"] = "En planificación"
                datos["fecha_inicio"] = date.today().isoformat()

                resultado = insertar("proyectos", datos)

                if not resultado:

                    st.error(
                        "No se pudo confirmar la duplicación."
                    )

                    return

                notificar(
                    f"Proyecto {nuevo_nombre} "
                    "duplicado correctamente."
                )

            except Exception as error:

                if "23505" in str(error):

                    st.warning(
                        "Ya existe un proyecto con ese nombre."
                    )

                else:

                    st.error(
                        "No fue posible duplicar el proyecto."
                    )

    elif accion == "Eliminar":

        tablas = {
            "riesgos": "Evaluaciones de riesgos",
            "arco_electrico": "Evaluaciones de arco eléctrico",
            "etiquetas": "Etiquetas",
            "loto": "Documentación LOTO",
            "permisos": "Permisos de trabajo"
        }

        vinculados = {
            nombre: len(consultar(
                tabla,
                {"proyecto_id": seleccionado}
            ))
            for tabla, nombre in tablas.items()
        }

        if sum(vinculados.values()) > 0:

            st.warning(
                "El proyecto contiene registros técnicos "
                "asociados y no puede eliminarse."
            )

            for nombre, cantidad in vinculados.items():

                if cantidad:

                    st.write(f"**{nombre}:** {cantidad}")

        else:

            st.warning("Esta acción es permanente.")

            confirmar = st.checkbox(
                "Confirmo la eliminación del proyecto",
                key=f"eliminar_proyecto_{seleccionado}"
            )

            if st.button(
                "Eliminar proyecto",
                disabled=not confirmar
            ):

                try:

                    resultado = eliminar(
                        "proyectos",
                        seleccionado
                    )

                    if not resultado:

                        st.error(
                            "No se pudo confirmar la eliminación."
                        )

                        return

                    if st.session_state.get(
                        "proyecto_activo"
                    ) == seleccionado:

                        st.session_state.pop(
                            "proyecto_activo", None
                        )

                    notificar(
                        f"Proyecto {proyecto['nombre']} "
                        "eliminado correctamente."
                    )

                except Exception:

                    st.error(
                        "No se pudo eliminar el proyecto."
                    )
