
import streamlit as st


def mostrar():

    st.title("Manual de uso")

    st.caption(
        "Electra Safe 360 | ElectraSafety Consultores"
    )

    st.write(
        "Guía práctica para registrar, consultar "
        "y exportar información de seguridad eléctrica."
    )

    st.info(
        "Orden recomendado: Clientes → Proyectos → "
        "Riesgos → Arco y EPP → Etiquetas → "
        "LOTO → Permisos."
    )

    secciones = {

        "Acceso y navegación": """

**Objetivo:** acceder al sistema y organizar el trabajo.

1. Ingrese el correo y la contraseña autorizados y pulse **Iniciar sesión**.
2. En Inicio, consulte los indicadores de clientes, proyectos, evaluaciones y documentos.
3. Utilice el menú lateral para abrir el módulo requerido.
4. Seleccione el proyecto de trabajo y compruebe el cliente y código asociados.
5. Guarde antes de cambiar de módulo. En la ventana de confirmación, elija Continuar o Permanecer.
6. Para finalizar, pulse Cerrar sesión y confirme.

**Si no puede ingresar:** revise sus credenciales y conexión. No comparta contraseñas.

""",

        "01. Clientes": """

**Objetivo:** registrar empresas y sus contactos.

1. Abra Clientes y seleccione **Registrar cliente**.
2. Complete la identificación de la empresa, actividad y ubicación según los campos disponibles.
3. Registre los datos de la persona de contacto y las observaciones pertinentes.
4. Pulse el botón de guardado y espere la notificación.
5. Seleccione **Consultar clientes** para localizar el registro.
6. Seleccione el cliente para consultar su información y proyectos asociados, o editar sus datos.
7. Antes de eliminar, revise las relaciones con proyectos y confirme únicamente si corresponde.

**Ejemplo:** Industrias Nova CR S.A. (empresa ficticia).

**Si no aparece el registro:** compruebe los filtros y que el guardado haya finalizado.

""",

        "02. Proyectos": """

**Objetivo:** organizar las evaluaciones y documentos de cada servicio de consultoría.

**Requisito:** contar con un cliente registrado.

1. Abra Proyectos y seleccione **Nuevo proyecto**.
2. Seleccione el cliente correcto.
3. Complete nombre, código, ubicación, fechas y demás campos disponibles.
4. Defina el alcance, responsable y estado del proyecto.
5. Guarde y vuelva a **Consultar proyectos**.
6. Localice el proyecto mediante los filtros y selecciónelo.
7. Utilice la opción para establecerlo como proyecto activo.
8. Revise el código del proyecto en el menú lateral antes de registrar datos técnicos.

**Resultado:** las herramientas técnicas podrán asociar sus registros al proyecto seleccionado.

El avance documental indica la existencia de registros, no su aprobación técnica.

**Si no aparece el cliente:** regístrelo primero en Clientes.

""",

        "03. Riesgos eléctricos": """

**Objetivo:** identificar peligros y documentar controles.

1. Seleccione el proyecto de trabajo.
2. Cree o seleccione una evaluación de riesgos.
3. Abra **Registrar peligro** e identifique el equipo, tarea y peligro.
4. Describa las consecuencias y personas expuestas según los campos disponibles.
5. Complete la evaluación inicial utilizando las escalas y criterios del módulo.
6. Documente las medidas de control siguiendo la jerarquía de controles.
7. Estime el riesgo residual considerando los controles propuestos; no lo confunda con un riesgo ya verificado.
8. Guarde y repita para cada peligro identificado.
9. Abra **Consultar resultados**, revise la tabla, edite registros si corresponde y descargue el informe disponible.

**Interpretación de resultados**

- Riesgo inicial: situación evaluada antes de los controles propuestos.
- Riesgo residual: estimación posterior a la incorporación de controles.
- Medidas de control: acciones propuestas para reducir la exposición y las consecuencias.

Revise especialmente los niveles altos o críticos.

**Si faltan resultados:** confirme que seleccionó la evaluación correcta.

""",

        "04. Arco eléctrico y EPP": """

**Objetivo:** documentar puntos de análisis y consultar el método de categorías cuando proceda.

1. Seleccione el proyecto y abra **Nueva evaluación**.
2. Seleccione CA o CC e identifique equipo, tipo, ubicación, tarea y condición.
3. Registre tensión nominal (V), corriente de falla disponible (kA), tiempo de despeje (s) y distancia de trabajo (mm). No confunda unidades.
4. Registre elevación, tipo de parte expuesta y fuentes documentales.
5. Revise las condiciones de aplicación y marque únicamente las verificaciones efectivamente realizadas. Documente la evidencia.
6. Pulse **Evaluar parámetros**. Si el método no aplica, no invente una categoría: solicite revisión especializada.
7. Revise por separado los resultados de arco y choque eléctrico. Guarde la evaluación.
8. En **Consultar y editar**, seleccione el punto, revise los datos, actualice si corresponde y descargue el informe.
9. En **Selección de EPP**, seleccione una evaluación con categoría asignada y consulte la ilustración y conjunto de referencia.
10. Ingrese la clasificación documentada del conjunto, identifique los equipos seleccionados y registre la revisión documental. Descargue la ficha CSV si está disponible.

**Explicación de los parámetros**

- Tensión nominal: tensión de funcionamiento del sistema eléctrico.
- Corriente de falla disponible: corriente de cortocircuito disponible en el punto evaluado.
- Tiempo de despeje: duración asociada a la actuación de la protección eléctrica.
- Distancia de trabajo: distancia considerada entre la persona y la fuente potencial de arco.
- Fuente de datos: documentación técnica que respalda los parámetros ingresados.

**Interpretación de resultados**

- Categoría: conjunto de protección contra arco asociado al método de tablas.
- Clasificación mínima: valor mínimo de protección contra arco indicado para la categoría.
- Frontera de arco: distancia de referencia asociada al peligro térmico.
- Aproximación limitada y restringida: fronteras relacionadas con el peligro de choque eléctrico.

Alcanzar la clasificación mínima contra arco no confirma la conformidad de todo el conjunto ni su aislamiento dieléctrico.

**Importante:** los valores programados son preliminares y requieren cotejo normativo. La ficha CSV no equivale a un registro independiente guardado en Supabase.

""",

        "05. Etiquetas eléctricas": """

**Objetivo:** preparar etiquetas de advertencia e identificación de peligros eléctricos.

1. Seleccione el proyecto y abra **Desde evaluación** para utilizar un punto interno.
2. Localice la evaluación y revise equipo, ubicación, tensión, categoría y frontera disponibles.
3. Seleccione los registros que desea utilizar y revise la vista previa antes de guardar o descargar.
4. Para información procedente de un estudio externo, abra **Datos externos**, complete los datos y documente su fuente y revisión.
5. Genere la vista previa y compruebe que el contenido coincide con la documentación de origen.
6. Guarde la etiqueta y abra **Etiquetas guardadas** para consultar, filtrar o descargar registros individuales o por lotes.
7. Si cambia una evaluación, compare manualmente el punto y revisión de origen con la etiqueta antes de volver a emitirla.

**Tipos de etiquetas**

- Internas: utilizan información procedente de las evaluaciones registradas en la aplicación.
- Externas: utilizan información respaldada por documentación técnica externa.

**Si no aparece una evaluación:** revise el proyecto y compruebe que el punto se guardó.

No imprima etiquetas con datos incompletos o desactualizados.

""",

        "06. Bloqueo y etiquetado LOTO": """

**Objetivo:** documentar la gestión de energías peligrosas durante las actividades de mantenimiento.

1. Seleccione el proyecto y abra **Catálogo de dispositivos**.
2. Consulte las ilustraciones, función y compatibilidad de los dispositivos.
3. Abra **Política y procedimiento** y seleccione **Crear documento**.
4. Complete la identificación, alcance, responsabilidades, fuentes de energía y demás apartados del formulario.
5. Documente las medidas y verificaciones específicas del equipo con personal calificado; no utilice una plantilla como procedimiento validado.
6. Guarde el documento y utilice **Consultar y editar** para recuperarlo o exportarlo.
7. Abra **Etiquetas LOTO**, complete los datos solicitados y genere la vista previa.
8. Revise, guarde y descargue las etiquetas según las opciones disponibles.

**Herramientas disponibles**

- Catálogo ilustrado de dispositivos.
- Documentación de políticas y procedimientos.
- Generación de etiquetas de bloqueo.
- Consulta y exportación de documentos.

**Importante:** compruebe la compatibilidad real de cada dispositivo y la revisión del procedimiento antes de cualquier aplicación.

""",

        "07. Permisos de trabajo": """

**Objetivo:** documentar las condiciones y requisitos asociados a los trabajos eléctricos.

1. Seleccione el proyecto de trabajo.
2. Seleccione el tipo de permiso: trabajo eléctrico energizado o permiso interno de trabajo desenergizado.
3. Cuando corresponda, vincule los registros de riesgos, arco eléctrico o procedimiento LOTO disponibles.
4. Seleccione **Crear documento** y complete la identificación, actividad, responsables, condiciones y medidas de protección.
5. Documente las justificaciones y verificaciones exigidas por el tipo de permiso.
6. Revise la información importada y los campos pendientes.
7. Guarde el documento como borrador y utilice **Consultar y editar** para recuperarlo.
8. Descargue el PDF y compruebe que la información corresponde al proyecto y revisión correctos.

**Información que debe revisarse**

- Identificación del equipo.
- Descripción de la actividad.
- Responsables del trabajo.
- Evaluaciones técnicas relacionadas.
- Medidas de protección.
- Verificaciones y autorizaciones correspondientes.

**Importante:** un documento generado por la aplicación no autoriza por sí mismo un trabajo eléctrico.

""",

        "Guardado, exportación y problemas frecuentes": """

**Almacenamiento de información**

1. Pulse Guardar o Actualizar antes de salir de un formulario.
2. Espere la notificación y consulte el registro para verificar que se almacenó.
3. Para exportar, seleccione el documento guardado y pulse la opción de descarga correspondiente.
4. Abra el archivo descargado y revise identificación, contenido y legibilidad.
5. Si no aparece un registro, compruebe el proyecto activo y los filtros.
6. Si aparece un error, conserve una captura y comuníquelo al equipo de desarrollo. No repita operaciones de guardado sin comprobar si ya se registraron.

**Problemas frecuentes**

| Problema | Posible solución |
|---|---|
| No aparece un cliente | Revise los filtros de búsqueda. |
| No aparece un proyecto | Compruebe que se guardó correctamente. |
| No aparecen evaluaciones | Verifique el proyecto activo. |
| El método de tablas no aplica | Revise los parámetros y condiciones documentadas. |
| No aparece una categoría | No asigne una categoría arbitrariamente. |
| No se genera un documento | Revise los campos obligatorios y los registros asociados. |
| No se guardan los datos | Compruebe la conexión y los mensajes del sistema. |

**Nota:** descargar un archivo no implica guardar los cambios del formulario.

""",

        "Limitaciones de la aplicación": """

Electra Safe 360 es una herramienta académica de apoyo a la gestión de la seguridad eléctrica.

No sustituye estudios especializados, la normativa aplicable ni la revisión por personal calificado.

No utilice datos confidenciales durante demostraciones.

Las etiquetas, permisos y resultados requieren validación antes de cualquier uso real.

"""

    }

    for titulo, contenido in secciones.items():

        with st.expander(titulo):

            st.markdown(contenido)

    st.divider()

    st.caption(
        "Referencia académica: NFPA 70E, edición 2027."
    )

    st.caption(
        "Tecnologías: Python, Streamlit, Supabase, "
        "GitHub y ReportLab. IA utilizada: ChatGPT."
    )
