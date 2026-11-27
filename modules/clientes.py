import streamlit as st

from modules.reportes import generar_pdf
import pandas as pd

from database import consultar, insertar, actualizar, eliminar


def formulario_cliente(cliente=None):
    cliente = cliente or {}
    identificador = cliente.get("id", "nuevo")

    with st.form(f"formulario_cliente_{identificador}"):
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

        st.caption("* Campo obligatorio.")

        guardar = st.form_submit_button(
            "Guardar cliente",
            type="primary",
            use_container_width=True
        )

        if not guardar:
            return

        if not nombre.strip():
            st.error("Debes indicar el nombre de la empresa.")
            return

        if correo and (
            "@" not in correo
            or "." not in correo.split("@")[-1]
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
            existentes = consultar("clientes")

            for existente in existentes:
                if existente["id"] == cliente.get("id"):
                    continue

                mismo_nombre = (
                    existente["nombre_empresa"].strip().casefold()
                    == nombre.strip().casefold()
                )

                misma_identificacion = (
                    bool(identificacion.strip())
                    and
                    (existente.get("identificacion") or "")
                    .strip().casefold()
                    == identificacion.strip().casefold()
                )

                if mismo_nombre or misma_identificacion:
                    st.warning(
                        "Este cliente ya se encuentra registrado. "
                        "Puedes consultar o editar su información "
                        "desde la lista de clientes."
                    )
                    return

            if cliente.get("id"):
                resultado = actualizar(
                    "clientes",
                    cliente["id"],
                    datos
                )

                mensaje = (
                    f"Cliente {nombre} actualizado correctamente."
                )

            else:
                resultado = insertar("clientes", datos)

                mensaje = (
                    f"Cliente {nombre} registrado exitosamente."
                )

            if not resultado:
                st.error("No se pudo confirmar el guardado.")
                return

            st.session_state.aviso_cliente = mensaje
            st.session_state.cliente_guardado = True

            st.rerun()

        except Exception as error:
            if "23505" in str(error):
                st.warning(
                    "Este cliente ya se encuentra registrado."
                )

            else:
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

    if st.session_state.pop("cliente_guardado", False):
        st.session_state["accion_clientes"] = (
            "Consultar clientes"
        )

        st.session_state["administrar_cliente"] = (
            "Ver información"
        )

    if "aviso_cliente" in st.session_state:
        mensaje = st.session_state.pop("aviso_cliente")

        st.success(mensaje)
        st.toast(mensaje, icon="✅")

    clientes = consultar("clientes")
    proyectos_totales = consultar("proyectos")

    c1, c2 = st.columns(2)

    c1.metric("Clientes registrados", len(clientes))
    c2.metric("Proyectos registrados", len(proyectos_totales))

    opcion = st.radio(
        "Selecciona una acción",
        ["Consultar clientes", "Registrar cliente"],
        horizontal=True,
        key="accion_clientes"
    )

    st.divider()

    if opcion == "Registrar cliente":
        formulario_cliente()
        return

    if not clientes:
        st.info("Todavía no hay clientes registrados.")
        return

    busqueda = st.text_input(
        "Buscar cliente",
        placeholder="Empresa, identificación, correo o contacto"
    )

    filtrados = [
        c for c in clientes
        if busqueda.strip().casefold() in " ".join([
            str(c.get("nombre_empresa") or ""),
            str(c.get("identificacion") or ""),
            str(c.get("contacto") or ""),
            str(c.get("correo") or "")
        ]).casefold()
    ]

    if not filtrados:
        st.warning("No se encontraron clientes.")
        return

    columnas = {
        "nombre_empresa": "Empresa",
        "identificacion": "Identificación",
        "actividad_economica": "Actividad económica",
        "contacto": "Contacto",
        "telefono": "Teléfono",
        "correo": "Correo"
    }

    tabla = pd.DataFrame(filtrados)

    st.dataframe(
        tabla[list(columnas)].rename(columns=columnas),
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "Descargar listado de clientes",
        data=tabla[list(columnas)]
        .rename(columns=columnas)
        .to_csv(index=False)
        .encode("utf-8-sig"),
        file_name="clientes_electrasafety.csv",
        mime="text/csv",
        on_click="ignore",
    )

    informe = [
        (str(cliente.get("nombre_empresa") or "Cliente"), {
            **{etiqueta: cliente.get(campo) for campo, etiqueta in columnas.items()},
            "Dirección": cliente.get("direccion"),
            "Observaciones": cliente.get("observaciones")
        })
        for cliente in filtrados
    ]
    st.download_button(
        "Descargar listado de clientes en PDF",
        generar_pdf("Listado de clientes", None, informe),
        "clientes_electrasafety.pdf", "application/pdf", on_click="ignore"
    )

    st.divider()

    opciones = {c["id"]: c for c in filtrados}

    seleccionado = st.selectbox(
        "Seleccionar cliente",
        list(opciones),
        format_func=lambda x: (
            opciones[x]["nombre_empresa"]
            + " | " + x[:8]
        )
    )

    cliente = opciones[seleccionado]

    accion = st.radio(
        "Administrar cliente",
        ["Ver información", "Editar", "Eliminar"],
        horizontal=True,
        key="administrar_cliente"
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
                ].rename(columns={
                    "codigo": "Código",
                    "nombre": "Proyecto",
                    "estado": "Estado"
                }),
                hide_index=True,
                use_container_width=True
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
                    resultado = eliminar(
                        "clientes",
                        seleccionado
                    )

                    if not resultado:
                        st.error(
                            "No se pudo confirmar la eliminación."
                        )
                        return

                    st.session_state.aviso_cliente = (
                        f"Cliente {cliente['nombre_empresa']} "
                        "eliminado correctamente."
                    )

                    st.session_state.cliente_guardado = True

                    st.rerun()

                except Exception:
                    st.error("No se pudo eliminar el cliente.")
