import streamlit as st
import pandas as pd

from datetime import date
from numbers import Integral
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

METODO = "Matriz P × S 5 × 5 de uso académico"
CRITERIOS_PROBABILIDAD = {
    1: "Exposición excepcional y controles existentes eficaces.",
    2: "Exposición ocasional y condiciones poco favorables al daño.",
    3: "El daño es plausible en las condiciones observadas.",
    4: "Exposición frecuente o controles de eficacia limitada.",
    5: "Exposición recurrente con condiciones que favorecen el daño."
}
PELIGROS = [
    "Choque eléctrico", "Arco eléctrico", "Quemaduras por contacto",
    "Onda de presión", "Incendio o explosión", "Energía almacenada", "Otro"
]
NIVELES = (
    (4, "Bajo", "#238B57", "Mantener controles y revisar."),
    (9, "Moderado", "#D4A017", "Evaluar medidas adicionales."),
    (16, "Alto", "#E67E22", "Reducir el riesgo antes de iniciar."),
    (25, "Crítico", "#C0392B", "No iniciar bajo estas condiciones.")
)


def nivel_riesgo(valor):
    return next((nivel, color, criterio)
                for maximo, nivel, color, criterio in NIVELES if valor <= maximo)


def escala(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, str) and valor.strip() in {"1", "2", "3", "4", "5"}:
        valor = int(valor)
    return int(valor) if isinstance(valor, Integral) and 1 <= valor <= 5 else None



def clasificar(p, s):

    p, s = escala(p), escala(s)
    if p is None or s is None:
        raise ValueError("La probabilidad y la severidad deben ser enteros de 1 a 5.")
    valor = p * s
    return (valor, *nivel_riesgo(valor))


def revisar_detalle(detalle):
    resultado = dict(detalle)
    for etapa in ("inicial", "residual"):
        p, s = (escala(detalle.get(f"{letra} {etapa}")) for letra in ("P", "S"))
        valor, nivel, _, criterio = (
            clasificar(p, s) if p is not None and s is not None
            else (None, "Pendiente de revisión", "", "Revisar las escalas del registro.")
        )
        resultado.update({
            f"Riesgo {etapa}": valor,
            f"Nivel {etapa}": nivel,
            f"Criterio {etapa}": criterio
        })
    verificado = resultado.get("Controles verificados") == "Sí" and bool(
        str(resultado.get("Evidencia de verificación") or "").strip()
    )
    resultado["Interpretación residual"] = (
        "Valoración posterior documentada" if verificado
        else "Estimación condicionada a implementar y comprobar los controles"
    )
    return resultado


def tarjeta_riesgo(p, s):

    if escala(p) is None or escala(s) is None:
        st.warning("Puntuación incompleta. Edite el registro para revisarla.")
        return
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

        _, color, _ = nivel_riesgo(valor)
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

    st.caption(
        "P × S usa escalas ordinales académicas. El artículo 110.3(H) establece "
        "el proceso y la jerarquía. El Anexo F ofrece orientación informativa."
    )


def nueva_evaluacion(proyecto):

    with st.form(f"nueva_evaluacion_{proyecto['id']}"):

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
    clave = f"{proyecto['id']}_{evaluacion['id']}_{registro.get('id', 'nuevo')}"

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
            PELIGROS,
            index=PELIGROS.index(anterior["Peligro"])
            if anterior.get("Peligro") in PELIGROS else None
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

        error_humano = st.text_area(
            "Posible error humano y consecuencias *",
            value=anterior.get("Error humano", "")
        )

        st.subheader("2. Evaluación inicial")
        st.caption("Valore la tarea bajo los controles existentes. Justifique P y S por separado.")

        c1, c2 = st.columns(2)

        p = c1.selectbox(
            "Probabilidad inicial",
            list(PROBABILIDAD),
            format_func=lambda x: f"{x} - {PROBABILIDAD[x]}",
            index=escala(anterior["P inicial"]) - 1 if escala(anterior.get("P inicial")) is not None else None
        )

        s = c2.selectbox(
            "Severidad inicial",
            list(SEVERIDAD),
            format_func=lambda x: f"{x} - {SEVERIDAD[x]}",
            index=escala(anterior["S inicial"]) - 1 if escala(anterior.get("S inicial")) is not None else None
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

        justificacion_jerarquia = st.text_area(
            "Decisión sobre eliminación y controles de mayor jerarquía *",
            value=anterior.get("Justificación de jerarquía", ""),
            help="Indique la medida adoptada o por qué los niveles superiores resultan insuficientes o inviables."
        )

        responsable = st.text_input(
            "Responsable de implementación *",
            value=anterior.get("Responsable", "")
        )

        try:
            fecha_anterior = date.fromisoformat(str(anterior.get("Plazo") or ""))
        except ValueError:
            fecha_anterior = date.today()
        plazo = st.date_input("Fecha prevista de implementación", value=fecha_anterior)

        st.subheader("4. Riesgo residual estimado")

        c3, c4 = st.columns(2)

        pr = c3.selectbox(
            "Probabilidad residual",
            list(PROBABILIDAD),
            format_func=lambda x: f"{x} - {PROBABILIDAD[x]}",
            index=escala(anterior["P residual"]) - 1 if escala(anterior.get("P residual")) is not None else None
        )

        sr = c4.selectbox(
            "Severidad residual",
            list(SEVERIDAD),
            format_func=lambda x: f"{x} - {SEVERIDAD[x]}",
            index=escala(anterior["S residual"]) - 1 if escala(anterior.get("S residual")) is not None else None
        )

        justificacion = st.text_area(
            "Justificación del riesgo residual *",
            value=anterior.get("Justificación residual", "")
        )

        verificado = st.checkbox(
            "Los controles han sido implementados y verificados",
            value=anterior.get("Controles verificados") == "Sí"
        )

        evidencia_verificacion = st.text_area(
            "Evidencia de implementación y verificación",
            value=anterior.get("Evidencia de verificación", ""),
            help="Registre quién verificó, cuándo y con qué evidencia."
        )

        guardar = st.form_submit_button(
            "Evaluar y guardar riesgo",
            type="primary",
            use_container_width=True
        )

    if not guardar:
        return

    if None in (p, s, pr, sr):
        st.error("Selecciona las cuatro valoraciones de probabilidad y severidad.")
        return

    if not all([
        equipo.strip(), tarea.strip(), peligro,
        mecanismo.strip(), responsable.strip(),
        fundamento.strip(), justificacion.strip(), error_humano.strip(),
        justificacion_jerarquia.strip()
    ]):

        st.error("Completa todos los campos obligatorios.")
        return

    if not any(v.strip() for v in medidas.values()):

        st.error("Documenta al menos una medida de control.")
        return

    if verificado and not evidencia_verificacion.strip():
        st.error("Documenta la evidencia para marcar los controles como verificados.")
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
        "Error humano": error_humano,
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
        "Justificación de jerarquía": justificacion_jerarquia,
        "Responsable": responsable,
        "Plazo": plazo.isoformat(),
        "P residual": pr,
        "S residual": sr,
        "Riesgo residual": residual,
        "Nivel residual": nivel_r,
        "Criterio residual": criterio_r,
        "Justificación residual": justificacion,
        "Controles verificados": "Sí" if verificado else "No",
        "Evidencia de verificación": evidencia_verificacion,
        "Interpretación residual": (
            "Valoración posterior documentada" if verificado
            else "Estimación condicionada a implementar y comprobar los controles"
        )
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
            st.write(f"Probabilidad {numero} · {descripcion}. {CRITERIOS_PROBABILIDAD[numero]}")

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
        {"proyecto_id": proyecto["id"], "evaluacion_id": seleccion}
    )

    detalles = [
        revisar_detalle(r.get("detalle") or {})
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
            "Anexo F informativo. Escala y umbrales 5 × 5 definidos para el ejercicio académico."
        )

        st.download_button(
            "Descargar informe PDF",
            pdf,
            "evaluacion_riesgos.pdf",
            "application/pdf",
            type="primary",
            on_click="ignore",
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
                detalle.get("P inicial"),
                detalle.get("S inicial")
            )

        with c2:
            st.write("**Riesgo residual**")
            tarjeta_riesgo(
                detalle.get("P residual"),
                detalle.get("S residual")
            )

        if revisar_detalle(detalle)["Interpretación residual"] != "Valoración posterior documentada":

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
