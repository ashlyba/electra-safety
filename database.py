
import streamlit as st
import logging

from datetime import datetime
from supabase import create_client


TABLAS = {
    "clientes",
    "proyectos",
    "evaluaciones",
    "riesgos",
    "arco_electrico",
    "etiquetas",
    "loto",
    "permisos"
}


NOMBRES_TABLAS = {
    "clientes": "clientes",
    "proyectos": "proyectos",
    "evaluaciones": "evaluaciones",
    "riesgos": "riesgos eléctricos",
    "arco_electrico": "evaluaciones de arco eléctrico",
    "etiquetas": "etiquetas",
    "loto": "documentos LOTO",
    "permisos": "permisos de trabajo"
}


def registrar_conexion(correcta):

    st.session_state["conexion_correcta"] = correcta

    st.session_state["ultima_conexion"] = (
        datetime.now().strftime("%H:%M:%S")
    )


def estado_conexion():

    return st.session_state.get(
        "conexion_correcta",
        None
    )


def conectar():

    if "supabase_cliente" not in st.session_state:

        try:

            st.session_state.supabase_cliente = (
                create_client(
                    st.secrets["supabase"]["url"],
                    st.secrets["supabase"]["key"]
                )
            )

        except Exception:

            registrar_conexion(False)

            logging.exception(
                "Error al inicializar Supabase"
            )

            raise

    return st.session_state.supabase_cliente


def iniciar_sesion(correo, password):

    with st.spinner("Verificando credenciales..."):

        try:

            respuesta = conectar().auth.sign_in_with_password({
                "email": correo,
                "password": password
            })

            if respuesta.user:

                st.session_state.usuario = (
                    respuesta.user.email
                )

                registrar_conexion(True)

                return True

            return False

        except Exception:

            logging.exception(
                "Error de autenticación"
            )

            raise


def cerrar_sesion():

    with st.spinner("Cerrando sesión..."):

        conectar().auth.sign_out()

        st.session_state.clear()


def validar_tabla(tabla):

    if tabla not in TABLAS:

        raise ValueError(
            "Tabla no permitida."
        )


def consultar(tabla, filtros=None):

    validar_tabla(tabla)

    nombre = NOMBRES_TABLAS[tabla]

    registros = []
    inicio = 0
    limite = 500

    with st.spinner(f"Consultando {nombre}..."):

        try:

            while True:

                consulta = conectar().table(
                    tabla
                ).select("*")

                if filtros:

                    for campo, valor in filtros.items():

                        consulta = consulta.eq(
                            campo,
                            valor
                        )

                respuesta = consulta.order(
                    "fecha_creacion",
                    desc=True
                ).order(
                    "id"
                ).range(
                    inicio,
                    inicio + limite - 1
                ).execute()

                datos = respuesta.data or []

                registros.extend(datos)

                if len(datos) < limite:

                    break

                inicio += limite

            registrar_conexion(True)

            return registros

        except Exception:

            registrar_conexion(False)

            logging.exception(
                "Error al consultar %s",
                tabla
            )

            raise


def insertar(tabla, datos):

    validar_tabla(tabla)

    with st.spinner(
        "Guardando información. Espere un momento..."
    ):

        try:

            respuesta = conectar().table(
                tabla
            ).insert(
                datos
            ).execute()

            registrar_conexion(True)

            return respuesta.data

        except Exception:

            logging.exception(
                "Error al insertar en %s",
                tabla
            )

            st.toast(
                "No se pudo guardar la información. "
                "Revise los datos y la conexión."
            )

            raise


def actualizar(tabla, registro_id, datos):

    validar_tabla(tabla)

    with st.spinner(
        "Actualizando información..."
    ):

        try:

            respuesta = conectar().table(
                tabla
            ).update(
                datos
            ).eq(
                "id",
                registro_id
            ).execute()

            registrar_conexion(True)

            return respuesta.data

        except Exception:

            logging.exception(
                "Error al actualizar %s",
                tabla
            )

            st.toast(
                "No fue posible actualizar el registro."
            )

            raise


def eliminar(tabla, registro_id):

    validar_tabla(tabla)

    with st.spinner(
        "Eliminando registro..."
    ):

        try:

            respuesta = conectar().table(
                tabla
            ).delete().eq(
                "id",
                registro_id
            ).execute()

            registrar_conexion(True)

            return respuesta.data

        except Exception:

            logging.exception(
                "Error al eliminar de %s",
                tabla
            )

            st.toast(
                "No fue posible eliminar el registro. "
                "Revise si tiene información asociada."
            )

            raise


def contar(tabla):

    validar_tabla(tabla)

    try:

        respuesta = conectar().table(
            tabla
        ).select(
            "id",
            count="exact"
        ).limit(
            1
        ).execute()

        registrar_conexion(True)

        return respuesta.count or 0

    except Exception:

        registrar_conexion(False)

        logging.exception(
            "Error al contar registros de %s",
            tabla
        )

        raise
