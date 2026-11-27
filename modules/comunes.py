
import streamlit as st
import logging

from html import escape
from database import consultar, contar


MODULOS_TECNICOS = {
    "evaluaciones": "Riesgos eléctricos",
    "arco_electrico": "Arco eléctrico y EPP",
    "etiquetas": "Etiquetas eléctricas",
    "loto": "Bloqueo y etiquetado LOTO",
    "permisos": "Permisos de trabajo"
}


AYUDAS = {

    "riesgos": (
        "Seleccione una evaluación, registre los "
        "peligros eléctricos y documente las "
        "medidas de control correspondientes."
    ),

    "arco_electrico": (
        "Identifique el equipo e ingrese los "
        "parámetros respaldados por documentación "
        "técnica. Verifique las condiciones de "
        "aplicación antes de asignar una categoría."
    ),

    "etiquetas": (
        "Seleccione una evaluación guardada o "
        "registre información externa documentada. "
        "Revise la etiqueta antes de imprimir."
    ),

    "loto": (
        "Consulte los dispositivos de bloqueo "
        "y documente los procedimientos y "
        "etiquetas correspondientes."
    ),

    "permisos": (
        "Seleccione el tipo de permiso, complete "
        "los requisitos y revise la documentación "
        "asociada antes de exportar."
    )

}


def seleccionar_proyecto(clave):

    try:

        proyectos = consultar("proyectos")

        clientes = {
            c["id"]: c["nombre_empresa"]
            for c in consultar("clientes")
        }

    except Exception:

        logging.exception(
            "Error al consultar proyectos"
        )

        st.error(
            "No fue posible recuperar los proyectos. "
            "Compruebe la conexión e intente nuevamente."
        )

        return None

    if not proyectos:

        st.warning(
            "Para utilizar esta herramienta debe "
            "registrar primero un cliente y un proyecto."
        )

        return None

    opciones = {
        p["id"]: p
        for p in proyectos
    }

    ids = list(opciones)

    activo = st.session_state.get(
        "proyecto_activo"
    )

    if activo not in ids:

        activo = ids[0]

        st.session_state[
            "proyecto_activo"
        ] = activo

    widget = f"proyecto_{clave}"

    st.session_state[widget] = activo

    def cambiar_proyecto():

        st.session_state[
            "proyecto_activo"
        ] = st.session_state[widget]

    seleccionado = st.selectbox(
        "Proyecto de trabajo",
        ids,
        format_func=lambda x: (
            clientes.get(
                opciones[x]["cliente_id"],
                "Cliente"
            )
            + " | "
            + opciones[x]["nombre"]
        ),
        key=widget,
        on_change=cambiar_proyecto,
        help=(
            "Seleccione el proyecto al que desea "
            "asociar los registros de este módulo. "
            "Guarde los cambios antes de seleccionar otro."
        )
    )

    proyecto = opciones[seleccionado]

    cliente = clientes.get(
        proyecto.get("cliente_id"),
        "Cliente no registrado"
    )

    nombre = escape(
        str(proyecto.get("nombre", ""))
    )

    codigo = escape(
        str(proyecto.get("codigo", ""))
    )

    cliente = escape(str(cliente))

    st.html(f"""
    <div style="
        background:#0D2333;
        border-left:5px solid #FFB800;
        border-radius:10px;
        padding:18px 22px;
        margin-bottom:12px;
    ">
        <div style="
            color:#FFB800;
            font-size:11px;
            font-weight:700;
            letter-spacing:1px;
        ">
            PROYECTO ACTIVO
        </div>

        <div style="
            color:#FFFFFF;
            font-size:19px;
            font-weight:650;
            margin-top:5px;
        ">
            {nombre}
        </div>

        <div style="
            color:#D4E0E9;
            font-size:13px;
            margin-top:5px;
        ">
            {cliente} | {codigo}
        </div>
    </div>
    """)

    for modulo, ayuda in AYUDAS.items():

        if clave == modulo or clave.startswith(
            modulo + "_"
        ):

            with st.expander(
                "Ayuda rápida de esta herramienta"
            ):

                st.write(ayuda)

                st.caption(
                    "Consulte el Manual de uso "
                    "para obtener instrucciones "
                    "detalladas."
                )

            break

    return proyecto


def obtener_avance(proyecto_id):

    resultados = []

    for tabla, nombre in MODULOS_TECNICOS.items():

        registros = contar(
            tabla,
            {"proyecto_id": proyecto_id}
        )

        resultados.append({
            "Módulo": nombre,
            "Registros": registros,
            "Estado": (
                "Con registros"
                if registros
                else "Sin iniciar"
            )
        })

    iniciados = sum(
        r["Registros"] > 0
        for r in resultados
    )

    porcentaje = round(
        iniciados / len(MODULOS_TECNICOS) * 100
    )

    return porcentaje, resultados


def mostrar_avance(
    proyecto_id,
    compacto=False
):

    try:

        porcentaje, resultados = obtener_avance(
            proyecto_id
        )

    except Exception:

        logging.exception(
            "Error al calcular avance"
        )

        st.caption(
            "Avance temporalmente no disponible."
        )

        return

    st.caption("AVANCE DOCUMENTAL")

    st.progress(porcentaje / 100)

    st.write(
        f"{porcentaje}% de módulos iniciados"
    )

    if not compacto:

        st.dataframe(
            resultados,
            hide_index=True,
            use_container_width=True
        )

        st.caption(
            "El indicador representa la existencia "
            "de registros, no la aprobación técnica."
        )


def mostrar_estado_conexion():

    estado = st.session_state.get(
        "conexion_correcta"
    )

    if estado is True:

        color = "#16803C"

        mensaje = "Última consulta exitosa"

    elif estado is False:

        color = "#D97706"

        mensaje = "Problema en la última consulta"

    else:

        color = "#64748B"

        mensaje = "Conexión sin verificar"

    st.html(f"""
    <div style="
        display:flex;
        align-items:center;
        gap:8px;
        padding:8px 0;
        font-size:12px;
    ">
        <div style="
            background:{color};
            width:9px;
            height:9px;
            border-radius:50%;
        "></div>
        <span>{mensaje}</span>
    </div>
    """)


def notificar(clave, mensaje):

    st.session_state[
        f"aviso_{clave}"
    ] = mensaje

    st.rerun()


def mostrar_aviso(clave):

    mensaje = st.session_state.pop(
        f"aviso_{clave}",
        None
    )

    if mensaje:

        st.toast(mensaje)


def validar_obligatorios(campos):

    faltantes = []

    for nombre, valor in campos.items():

        if valor is None:

            faltantes.append(nombre)

        elif isinstance(valor, str):

            if not valor.strip():

                faltantes.append(nombre)

        elif isinstance(valor, (list, tuple, dict)):

            if not valor:

                faltantes.append(nombre)

    if faltantes:

        st.error(
            "Complete los siguientes campos "
            "obligatorios: "
            + ", ".join(faltantes)
        )

        st.toast(
            "Existen campos obligatorios pendientes."
        )

        return False

    return True


def marcar_cambios(clave):

    st.session_state[
        f"cambios_{clave}"
    ] = True


def limpiar_cambios(clave):

    st.session_state[
        f"cambios_{clave}"
    ] = False


def tiene_cambios(clave):

    return st.session_state.get(
        f"cambios_{clave}",
        False
    )


def limpiar_formulario(claves):

    for clave in claves:

        st.session_state.pop(
            clave,
            None
        )


@st.dialog(
    "Confirmar eliminación",
    dismissible=False
)
def confirmar_eliminacion(
    descripcion,
    accion,
    clave
):

    st.write(
        "¿Está seguro de que desea eliminar "
        "el siguiente registro?"
    )

    st.info(descripcion)

    st.warning(
        "Esta acción no se puede deshacer."
    )

    c1, c2 = st.columns(2)

    if c1.button(
        "Cancelar",
        key=f"cancelar_eliminar_{clave}",
        use_container_width=True
    ):

        st.rerun()

    if c2.button(
        "Eliminar registro",
        key=f"confirmar_eliminar_{clave}",
        type="primary",
        use_container_width=True
    ):

        try:

            accion()

            notificar(
                clave,
                "Registro eliminado correctamente."
            )

        except Exception:

            st.error(
                "No fue posible eliminar el registro. "
                "Compruebe si tiene información asociada."
            )


def advertencia_tecnica():

    st.caption(
        "Herramienta académica de apoyo. "
        "Los resultados requieren revisión por "
        "personal calificado antes de su aplicación real."
    )
