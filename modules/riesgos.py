
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
