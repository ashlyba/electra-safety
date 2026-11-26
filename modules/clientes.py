
import streamlit as st
import pandas as pd

from database import consultar, insertar, actualizar, eliminar


def formulario_cliente(cliente=None):

    cliente = cliente or {}

    with st.form("formulario_cliente"):

        st.subheader("Información de la empresa")

        c1, c2 = st.columns(2)

        with c1:
            nombre = st.text_input(
                "Nombre de la empresa *",
                value=cliente.get("nombre_empresa") or ""
            )

            identificacion = st.text_input(
                "Identificación jurídica",
                value=cliente.get("identificacion") or ""
            )

        with c2:
            actividad = st.text_input(
                "Actividad económica",
                value=cliente.get("actividad_economica") or ""
            )

            direccion = st.text_input(
                "Dirección",
                value=cliente.get("direccion") or ""
            )

        st.subheader("Persona de contacto")

        c3, c4 = st.columns(2)

        with c3:
            contacto = st.text_input(
                "Nombre del contacto",
                value=cliente.get("contacto") or ""
            )

            cargo = st.text_input(
                "Cargo",
                value=cliente.get("cargo_contacto") or ""
            )

        with c4:
            telefono = st.text_input(
                "Teléfono",
                value=cliente.get("telefono") or ""
            )

            correo = st.text_input(
                "Correo electrónico",
                value=cliente.get("correo") or ""
            )

        observaciones = st.text_area(
            "Observaciones",
            value=cliente.get("observaciones") or ""
        )

        st.caption(
            "* El nombre de la empresa es obligatorio "
            "para identificar al cliente y vincular "
            "sus proyectos."
        )

        guardar = st.form_submit_button(
            "Guardar cliente",
            type="primary"
        )

        if guardar:

            if not nombre.strip():
                st.error("Debes indicar el nombre de la empresa.")
                return

            if correo and (
                "@" not in correo or
                "." not in correo.split("@")[-1]
            ):
                st.error("Revisa el correo electrónico.")
                return

            datos = {
                "nombre_empresa": nombre.strip(),
                "identificacion": identificacion.strip(),
                "actividad_economica": actividad.strip(),
                "direccion": direccion.strip(),
                "contacto": contacto.strip(),
                "cargo_contacto": cargo.strip(),
                "telefono": telefono.strip(),
                "correo": correo.strip(),
                "observaciones": observaciones.strip()
            }

            try:
                if cliente.get("id"):
                    actualizar(
                        "clientes",
                        cliente["id"],
                        datos
                    )
                    st.session_state.aviso_cliente = (
                        "Cliente actualizado correctamente."
                    )
                else:
                    insertar("clientes", datos)
                    st.session_state.aviso_cliente = (
                        "Cliente registrado correctamente."
                    )

                st.rerun()

            except Exception:
                st.error(
                    "No fue posible guardar el cliente. "
                    "Revisa la conexión y los datos."
                )


def mostrar():

    st.title("01. Administración de clientes")

    st.write(
        "Registro y gestión de las empresas atendidas "
        "por ElectraSafety Consultores."
    )

    if "aviso_cliente" in st.session_state:
        st.success(st.session_state.pop("aviso_cliente"))

    clientes = consultar("clientes")

    c1, c2 = st.columns(2)

    c1.metric("Clientes registrados", len(clientes))
    c2.metric("Proyectos registrados", len(consultar("proyectos")))

    opcion = st.radio(
        "Selecciona una acción",
        ["Consultar clientes", "Registrar cliente"],
        horizontal=True,
        key="accion_clientes"
    )

    if opcion == "Registrar cliente":
        formulario_cliente()
        return

    if not clientes:
        st.info("Todavía no hay clientes registrados.")
        return

    busqueda = st.text_input(
        "Buscar cliente",
        placeholder="Empresa, identificación o contacto"
    )

    filtrados = [
        c for c in clientes
        if busqueda.lower() in " ".join([
            str(c.get("nombre_empresa") or ""),
            str(c.get("identificacion") or ""),
            str(c.get("contacto") or "")
        ]).lower()
    ]

    if not filtrados:
        st.warning("No se encontraron clientes.")
        return

    tabla = pd.DataFrame(filtrados)

    columnas = {
        "nombre_empresa": "Empresa",
        "identificacion": "Identificación",
        "actividad_economica": "Actividad económica",
        "contacto": "Contacto",
        "telefono": "Teléfono",
        "correo": "Correo"
    }

    st.dataframe(
        tabla[list(columnas)].rename(columns=columnas),
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    opciones = {c["id"]: c for c in filtrados}

    seleccionado = st.selectbox(
        "Seleccionar cliente",
        list(opciones),
        format_func=lambda x: (
            opciones[x]["nombre_empresa"] +
            " | " + x[:8]
        )
    )

    cliente = opciones[seleccionado]

    accion = st.radio(
        "Administrar cliente",
        ["Ver información", "Editar", "Eliminar"],
        horizontal=True
    )

    proyectos = consultar(
        "proyectos",
        {"cliente_id": seleccionado}
    )

    if accion == "Ver información":

        st.subheader(cliente["nombre_empresa"])

        campos = {
            "identificacion": "Identificación",
            "actividad_economica": "Actividad económica",
            "direccion": "Dirección",
            "contacto": "Contacto",
            "cargo_contacto": "Cargo",
            "telefono": "Teléfono",
            "correo": "Correo",
            "observaciones": "Observaciones"
        }

        for campo, etiqueta in campos.items():
            st.write(
                f"**{etiqueta}:** "
                f"{cliente.get(campo) or 'No registrado'}"
            )

        st.subheader("Proyectos asociados")

        if proyectos:
            st.dataframe(
                pd.DataFrame(proyectos)[
                    ["codigo", "nombre", "estado"]
                ],
                hide_index=True
            )
        else:
            st.info("Este cliente no tiene proyectos.")

    elif accion == "Editar":

        formulario_cliente(cliente)

    elif accion == "Eliminar":

        if proyectos:
            st.warning(
                "Este cliente tiene proyectos asociados "
                "y no puede eliminarse."
            )

            st.dataframe(
                pd.DataFrame(proyectos)[
                    ["codigo", "nombre", "estado"]
                ],
                hide_index=True
            )

        else:
            st.warning(
                "La eliminación del cliente es permanente."
            )

            confirmar = st.checkbox(
                "Confirmo que deseo eliminar este cliente",
                key=f"eliminar_cliente_{seleccionado}"
            )

            if st.button(
                "Eliminar cliente",
                disabled=not confirmar
            ):
                try:
                    eliminar("clientes", seleccionado)
                    st.session_state.aviso_cliente = (
                        "Cliente eliminado correctamente."
                    )
                    st.rerun()
                except Exception:
                    st.error("No se pudo eliminar el cliente.")
