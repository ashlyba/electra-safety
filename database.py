
import streamlit as st
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


def conectar():
    if "supabase_cliente" not in st.session_state:
        st.session_state.supabase_cliente = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )

    return st.session_state.supabase_cliente


def iniciar_sesion(correo, password):
    respuesta = conectar().auth.sign_in_with_password({
        "email": correo,
        "password": password
    })

    if respuesta.user:
        st.session_state.usuario = respuesta.user.email
        return True

    return False


def cerrar_sesion():
    conectar().auth.sign_out()
    st.session_state.clear()


def validar_tabla(tabla):
    if tabla not in TABLAS:
        raise ValueError("Tabla no permitida")


def consultar(tabla, filtros=None):
    validar_tabla(tabla)

    registros = []
    inicio = 0
    limite = 500

    while True:

        consulta = conectar().table(tabla).select("*")

        if filtros:
            for campo, valor in filtros.items():
                consulta = consulta.eq(campo, valor)

        respuesta = consulta.order(
            "fecha_creacion",
            desc=True
        ).order("id").range(
            inicio,
            inicio + limite - 1
        ).execute()

        datos = respuesta.data or []
        registros.extend(datos)

        if len(datos) < limite:
            break

        inicio += limite

    return registros


def insertar(tabla, datos):
    validar_tabla(tabla)

    return conectar().table(tabla).insert(
        datos
    ).execute().data


def actualizar(tabla, registro_id, datos):
    validar_tabla(tabla)

    return conectar().table(tabla).update(
        datos
    ).eq("id", registro_id).execute().data


def eliminar(tabla, registro_id):
    validar_tabla(tabla)

    return conectar().table(tabla).delete().eq(
        "id", registro_id
    ).execute().data


def contar(tabla):
    validar_tabla(tabla)

    respuesta = conectar().table(tabla).select(
        "id",
        count="exact"
    ).limit(1).execute()

    return respuesta.count or 0
