
import streamlit as st
import pandas as pd

from datetime import date
from database import consultar, insertar, actualizar, eliminar
from modules.comunes import (
    seleccionar_proyecto,
    notificar,
    mostrar_aviso,
    advertencia_tecnica
)
from modules.reportes import generar_pdf


PROBABILIDAD = {
    1: "Muy improbable",
    2: "Improbable",
    3: "Posible",
    4: "Probable",
    5: "Muy probable"
}

SEVERIDAD = {
    1: "Lesión leve",
    2: "Lesión con atención médica",
    3: "Lesión con incapacidad temporal",
    4: "Lesión grave o permanente",
    5: "Muerte o múltiples lesiones graves"
}

CONTROLES = [
    "Eliminación",
    "Sustitución",
    "Controles de ingeniería",
    "Concienciación",
    "Controles administrativos",
    "Equipo de protección personal"
]

METODO = "Matriz P x S 5x5 - propuesta académica"


def clasificar(p, s):

    valor = p * s

    if valor <= 4:
        nivel = "Bajo"
        color = "#238B57"
        criterio = "Mantener controles y revisar."

    elif valor <= 9:
        nivel = "Moderado"
        color = "#D4A017"
        criterio = "Evaluar medidas adicionales."

    elif valor <= 16:
        nivel = "Alto"
        color = "#E67E22"
        criterio = "Reducir el riesgo antes de iniciar."

    else:
        nivel = "Crítico"
        color = "#C0392B"
        criterio = "No iniciar bajo estas condiciones."

    return valor, nivel, color, criterio


def tarjeta_riesgo(p, s):

    valor, nivel, color, criterio = clasificar(p, s)

    st.markdown(
        f"""
        <div style="background:{color};
        color:white;padding:16px;border-radius:8px;">
        <strong>{nivel.upper()} | {valor}/25</strong>
        <p style="margin:5px 0 0;">{criterio}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def matriz_visual():

    datos = [
        [p * s for s in range(1, 6)]
        for p in range(5, 0, -1)
    ]

    tabla = pd.DataFrame(
        datos,
        index=[5, 4, 3, 2, 1],
        columns=[1, 2, 3, 4, 5]
    )

    def color_celda(valor):

        if valor <= 4:
            color = "#238B57"
        elif valor <= 9:
            color = "#D4A017"
        elif valor <= 16:
            color = "#E67E22"
        else:
            color = "#C0392B"

        return f"background-color:{color};color:white"

    st.caption("Filas: probabilidad | Columnas: severidad")

    st.dataframe(
        tabla.style.map(color_celda),
        use_container_width=True
    )

    st.caption(
        "Bajo: 1–4 | Moderado: 5–9 | "
        "Alto: 10–16 | Crítico: 17–25"
    )

    st.warning(
        "Escala académica propuesta, pendiente de "
        "validación metodológica. Un resultado bajo "
        "no autoriza por sí solo un trabajo eléctrico."
    )


def nueva_evaluacion(proyecto):

    with st.form("nueva_evaluacion"):

        nombre = st.text_input("Nombre de la evaluación *")
        area = st.text_input("Área o instalación")
        evaluador = st.text_input("Profesional evaluador")
        fecha = st.date_input("Fecha", date.today())
        observaciones = st.text_area("Observaciones")

        guardar = st.form_submit_button(
            "Crear evaluación",
            type="primary"
        )

        if guardar:

            if not nombre.strip():
                st.error("Indica el nombre de la evaluación.")
                return

            try:

                resultado = insertar("evaluaciones", {
                    "proyecto_id": proyecto["id"],
                    "nombre": nombre.strip(),
                    "area": area,
                    "evaluador": evaluador,
                    "fecha": fecha.isoformat(),
                    "metodologia": METODO,
                    "observaciones": observaciones
                })

                if resultado:
                    notificar(
                        "riesgos",
                        "Evaluación creada exitosamente."
                    )

            except Exception as error:

                if "23505" in str(error):
                    st.warning("Esta evaluación ya existe.")
                else:
                    st.error(str(error))


def formulario_riesgo(proyecto, evaluacion, registro=None):

    registro = registro or {}
    anterior = registro.get("detalle") or {}
    clave = str(registro.get("id", "nuevo"))

    with st.form("riesgo_" + clave):

        st.subheader("1. Identificación del peligro")

        equipo = st.text_input(
            "Equipo o instalación *",
            value=anterior.get("Equipo", "")
        )

        tarea = st.text_input(
            "Tarea evaluada *",
            value=anterior.get("Tarea", "")
        )

        peligro = st.selectbox(
            "Tipo de peligro",
            [
                "Choque eléctrico",
                "Arco eléctrico",
                "Quemaduras por contacto",
                "Onda de presión",
                "Incendio o explosión",
                "Energía almacenada",
                "Otro"
            ],
            index=None
        )

        mecanismo = st.text_area(
            "¿Cómo podría ocurrir el daño? *",
            value=anterior.get("Mecanismo de daño", "")
        )

        personas = st.text_input(
            "Personas expuestas",
            value=anterior.get("Personas expuestas", "")
        )

        entorno = st.text_area(
            "Condiciones del entorno y del equipo",
            value=anterior.get("Entorno", "")
        )

        existentes = st.text_area(
            "Controles existentes",
            value=anterior.get("Controles existentes", "")
        )

        st.subheader("2. Evaluación inicial")

        c1, c2 = st.columns(2)

        p = c1.selectbox(
            "Probabilidad inicial",
            list(PROBABILIDAD),
            format_func=lambda x: f"{x} - {PROBABILIDAD[x]}",
            index=int(anterior.get("P inicial", 3)) - 1
        )

        s = c2.selectbox(
            "Severidad inicial",
            list(SEVERIDAD),
            format_func=lambda x: f"{x} - {SEVERIDAD[x]}",
            index=int(anterior.get("S inicial", 3)) - 1
        )

        fundamento = st.text_area(
            "Justificación del riesgo inicial *",
            value=anterior.get("Justificación inicial", "")
        )

        st.subheader("3. Jerarquía de controles")

        medidas = {}

        for control in CONTROLES:

            medidas[control] = st.text_area(
                control,
                value=anterior.get(control, ""),
                placeholder="Medida propuesta o justificación"
            )

        responsable = st.text_input(
            "Responsable de implementación *",
            value=anterior.get("Responsable", "")
        )

        plazo = st.date_input("Fecha prevista de implementación")

        st.subheader("4. Riesgo residual estimado")

        c3, c4 = st.columns(2)

        pr = c3.selectbox(
            "Probabilidad residual",
            list(PROBABILIDAD),
            format_func=lambda x: f"{x} - {PROBABILIDAD[x]}",
            index=int(anterior.get("P residual", 2)) - 1
        )

        sr = c4.selectbox(
            "Severidad residual",
            list(SEVERIDAD),
            format_func=lambda x: f"{x} - {SEVERIDAD[x]}",
            index=int(anterior.get("S residual", 3)) - 1
        )

        justificacion = st.text_area(
            "Justificación del riesgo residual *",
            value=anterior.get("Justificación residual", "")
        )

        verificado = st.checkbox(
            "Los controles han sido implementados y verificados",
            value=anterior.get("Controles verificados") == "Sí"
        )

        guardar = st.form_submit_button(
            "Evaluar y guardar riesgo",
            type="primary",
            use_container_width=True
        )

    if not guardar:
        return

    if not all([
        equipo.strip(), tarea.strip(), peligro,
        mecanismo.strip(), responsable.strip(),
        fundamento.strip(), justificacion.strip()
    ]):

        st.error("Completa todos los campos obligatorios.")
        return

    if not any(v.strip() for v in medidas.values()):

        st.error("Documenta al menos una medida de control.")
        return

    inicial, nivel_i, _, criterio_i = clasificar(p, s)
    residual, nivel_r, _, criterio_r = clasificar(pr, sr)

    c1, c2 = st.columns(2)

    with c1:
        st.write("**Riesgo inicial**")
        tarjeta_riesgo(p, s)

    with c2:
        st.write("**Riesgo residual**")
        tarjeta_riesgo(pr, sr)

    detalle = {
        "Equipo": equipo,
        "Tarea": tarea,
        "Peligro": peligro,
        "Mecanismo de daño": mecanismo,
        "Personas expuestas": personas,
        "Entorno": entorno,
        "Controles existentes": existentes,
        "P inicial": p,
        "S inicial": s,
        "Riesgo inicial": inicial,
        "Nivel inicial": nivel_i,
        "Criterio inicial": criterio_i,
        "Justificación inicial": fundamento,
        **medidas,
        "Responsable": responsable,
        "Plazo": plazo.isoformat(),
        "P residual": pr,
        "S residual": sr,
        "Riesgo residual": residual,
        "Nivel residual": nivel_r,
        "Criterio residual": criterio_r,
        "Justificación residual": justificacion,
        "Controles verificados": "Sí" if verificado else "No"
    }

    datos = {
        "proyecto_id": proyecto["id"],
        "evaluacion_id": evaluacion["id"],
        "detalle": detalle
    }

    try:

        if registro.get("id"):

            resultado = actualizar(
                "riesgos",
                registro["id"],
                datos
            )

        else:

            resultado = insertar("riesgos", datos)

        if resultado:
            notificar("riesgos", "Riesgo guardado exitosamente.")

        else:
            st.error("No se pudo confirmar el guardado.")

    except Exception as error:

        st.error(str(error))


def mostrar():

    st.title("03. Evaluación de riesgos eléctricos")

    advertencia_tecnica()
    mostrar_aviso("riesgos")

    proyecto = seleccionar_proyecto("riesgos")

    if not proyecto:
        return

    with st.expander("Metodología y criterios de evaluación"):
        matriz_visual()

        for numero, descripcion in PROBABILIDAD.items():
            st.write(f"Probabilidad {numero}: {descripcion}")

        for numero, descripcion in SEVERIDAD.items():
            st.write(f"Severidad {numero}: {descripcion}")

    with st.expander("Crear nueva evaluación"):
        nueva_evaluacion(proyecto)

    evaluaciones = consultar(
        "evaluaciones",
        {"proyecto_id": proyecto["id"]}
    )

    if not evaluaciones:

        st.info("Crea una evaluación para comenzar.")
        return

    opciones = {e["id"]: e for e in evaluaciones}

    seleccion = st.selectbox(
        "Evaluación de riesgos",
        list(opciones),
        format_func=lambda x: opciones[x]["nombre"]
    )

    evaluacion = opciones[seleccion]

    registros = consultar(
        "riesgos",
        {"evaluacion_id": seleccion}
    )

    detalles = [
        r.get("detalle") or {}
        for r in registros
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Peligros registrados", len(registros))

    c2.metric(
        "Riesgos iniciales altos o críticos",
        sum(
            d.get("Nivel inicial") in ["Alto", "Crítico"]
            for d in detalles
        )
    )

    c3.metric(
        "Riesgos residuales altos o críticos",
        sum(
            d.get("Nivel residual") in ["Alto", "Crítico"]
            for d in detalles
        )
    )

    pestana1, pestana2 = st.tabs([
        "Registrar peligro",
        "Consultar resultados"
    ])

    with pestana1:
        formulario_riesgo(proyecto, evaluacion)

    with pestana2:

        if not registros:
            st.info("No hay peligros registrados.")
            return

        tabla = pd.DataFrame(detalles)

        columnas = [
            "Equipo", "Tarea", "Peligro",
            "Riesgo inicial", "Nivel inicial",
            "Riesgo residual", "Nivel residual"
        ]

        st.dataframe(
            tabla.reindex(columns=columnas),
            hide_index=True,
            use_container_width=True
        )

        secciones = [
            ("Datos de la evaluación", {
                "Evaluación": evaluacion["nombre"],
                "Área": evaluacion.get("area"),
                "Evaluador": evaluacion.get("evaluador"),
                "Metodología": METODO
            })
        ]

        for i, detalle in enumerate(detalles, 1):

            secciones.append(
                (f"Peligro {i}", detalle)
            )

        pdf = generar_pdf(
            "Informe de evaluación de riesgos eléctricos",
            proyecto,
            secciones,
            "NFPA 70E 2027: 110.3(H), 130.4 y 130.5. "
            "Matriz académica pendiente de validación."
        )

        st.download_button(
            "Descargar informe PDF",
            pdf,
            "evaluacion_riesgos.pdf",
            "application/pdf",
            type="primary"
        )

        opciones_r = {r["id"]: r for r in registros}

        riesgo_id = st.selectbox(
            "Seleccionar peligro",
            list(opciones_r),
            format_func=lambda x: (
                opciones_r[x].get("detalle", {}).get("Tarea", "")
                + " | "
                + opciones_r[x].get("detalle", {}).get("Peligro", "")
            )
        )

        registro = opciones_r[riesgo_id]
        detalle = registro.get("detalle") or {}

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Riesgo inicial**")
            tarjeta_riesgo(
                detalle["P inicial"],
                detalle["S inicial"]
            )

        with c2:
            st.write("**Riesgo residual**")
            tarjeta_riesgo(
                detalle["P residual"],
                detalle["S residual"]
            )

        if detalle.get("Controles verificados") != "Sí":

            st.warning(
                "El riesgo residual es una estimación. "
                "Los controles aún no han sido verificados."
            )

        accion = st.radio(
            "Administrar peligro",
            ["Ver información", "Editar", "Eliminar"],
            horizontal=True
        )

        if accion == "Ver información":

            for campo, valor in detalle.items():
                st.write(f"**{campo}:** {valor or '-'}")

        elif accion == "Editar":

            formulario_riesgo(
                proyecto, evaluacion, registro
            )

        elif accion == "Eliminar":

            confirmar = st.checkbox(
                "Confirmo la eliminación del peligro"
            )

            if st.button(
                "Eliminar peligro",
                disabled=not confirmar
            ):

                if eliminar("riesgos", riesgo_id):

                    notificar(
                        "riesgos",
                        "Peligro eliminado correctamente."
                    )
