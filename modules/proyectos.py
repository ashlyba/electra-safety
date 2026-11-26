
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


def formulario_proyecto(clientes, proyecto=None):

    proyecto = proyecto or {}

    opciones = {c["id"]: c["nombre_empresa"] for c in clientes}
    ids = list(opciones)

    indice = 0

    if proyecto.get("cliente_id") in ids:
        indice = ids.index(proyecto["cliente_id"])

    with st.form("formulario_proyecto"):

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
                ) if proyecto.get("fecha_inicio") else date.today()
            )

            final = st.date_input(
                "Fecha estimada de finalización",
                value=date.fromisoformat(
                    proyecto["fecha_final"]
                ) if proyecto.get("fecha_final") else None
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

        st.caption(
            "* El cliente y el nombre son obligatorios "
            "para identificar y vincular el proyecto."
        )

        if proyecto.get("codigo"):
            st.caption(
                "Código permanente: " + proyecto["codigo"]
            )

        guardar = st.form_submit_button(
            "Guardar proyecto",
            type="primary"
        )

        if guardar:

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
                "descripcion": descripcion,
                "ubicacion": ubicacion,
                "responsable": responsable,
                "fecha_inicio": inicio.isoformat(),
                "fecha_final": final.isoformat() if final else None,
                "estado": estado,
                "observaciones": observaciones
            }

            try:

                if proyecto.get("id"):
                    actualizar(
                        "proyectos",
                        proyecto["id"],
                        datos
                    )
                    st.session_state.aviso_proyecto = (
                        "Proyecto actualizado correctamente."
                    )
                else:
                    insertar("proyectos", datos)
                    st.session_state.aviso_proyecto = (
                        "Proyecto creado correctamente."
                    )

                st.rerun()

            except Exception:
                st.error("No fue posible guardar el proyecto.")


def mostrar():

    st.title("02. Gestión de proyectos")

    st.write(
        "Creación, seguimiento y administración "
        "de proyectos de seguridad eléctrica."
    )

    if "aviso_proyecto" in st.session_state:
        st.success(st.session_state.pop("aviso_proyecto"))

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

    filtrados = [
        p for p in proyectos
        if busqueda.lower() in " ".join([
            p["nombre"],
            p["codigo"],
            nombres_clientes.get(p["cliente_id"], "")
        ]).lower()
    ]

    if not filtrados:
        st.warning("No se encontraron proyectos.")
        return

    registros = [
        {
            "Código": p["codigo"],
            "Proyecto": p["nombre"],
            "Cliente": nombres_clientes.get(p["cliente_id"], ""),
            "Estado": p["estado"],
            "Inicio": p["fecha_inicio"]
        }
        for p in filtrados
    ]

    st.dataframe(
        pd.DataFrame(registros),
        hide_index=True,
        use_container_width=True
    )

    opciones = {p["id"]: p for p in filtrados}

    seleccionado = st.selectbox(
        "Seleccionar proyecto",
        list(opciones),
        format_func=lambda x: (
            opciones[x]["nombre"] +
            " | " + opciones[x]["codigo"]
        )
    )

    proyecto = opciones[seleccionado]

    accion = st.radio(
        "Administrar proyecto",
        ["Ver información", "Editar", "Duplicar", "Eliminar"],
        horizontal=True
    )

    if accion == "Ver información":

        st.subheader(proyecto["nombre"])

        st.write("**Código:**", proyecto["codigo"])
        st.write(
            "**Cliente:**",
            nombres_clientes.get(proyecto["cliente_id"], "")
        )
        st.write("**Estado:**", proyecto["estado"])
        st.write("**Ubicación:**", proyecto["ubicacion"] or "-")
        st.write("**Responsable:**", proyecto["responsable"] or "-")
        st.write("**Descripción:**", proyecto["descripcion"] or "-")
        st.write("**Fecha de inicio:**", proyecto["fecha_inicio"])
        st.write("**Fecha final:**", proyecto["fecha_final"] or "-")

        if st.button(
            "Establecer como proyecto activo",
            type="primary"
        ):
            st.session_state.proyecto_activo = seleccionado
            st.success("Proyecto activo seleccionado.")

    elif accion == "Editar":

        formulario_proyecto(clientes, proyecto)

    elif accion == "Duplicar":

        st.info(
            "Se creará un proyecto independiente "
            "con un nuevo código. En esta versión "
            "se copiarán los datos generales."
        )

        nuevo_nombre = st.text_input(
            "Nombre de la copia",
            value=proyecto["nombre"] + " - Copia"
        )

        if st.button("Duplicar proyecto"):

            if not nuevo_nombre.strip():
                st.error("Indica el nombre de la copia.")
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

            try:
                insertar("proyectos", datos)
                st.session_state.aviso_proyecto = (
                    "Proyecto duplicado correctamente."
                )
                st.rerun()
            except Exception:
                st.error("No fue posible duplicar el proyecto.")

    elif accion == "Eliminar":

        tablas = [
            "riesgos",
            "arco_electrico",
            "etiquetas",
            "loto",
            "permisos"
        ]

        vinculados = {
            tabla: len(consultar(
                tabla,
                {"proyecto_id": seleccionado}
            ))
            for tabla in tablas
        }

        if sum(vinculados.values()) > 0:

            st.warning(
                "El proyecto contiene registros técnicos "
                "asociados y no puede eliminarse."
            )

            st.write(vinculados)

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
                    eliminar("proyectos", seleccionado)

                    if st.session_state.get(
                        "proyecto_activo"
                    ) == seleccionado:
                        st.session_state.pop(
                            "proyecto_activo", None
                        )

                    st.session_state.aviso_proyecto = (
                        "Proyecto eliminado correctamente."
                    )

                    st.rerun()

                except Exception:
                    st.error("No se pudo eliminar el proyecto.")
