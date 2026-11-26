
import streamlit as st


def mostrar():

    st.title("Manual de uso")

    st.caption(
        "Electra Safe 360 | ElectraSafety Consultores"
    )

    st.write(
        "Sistema académico de apoyo a la gestión "
        "de la seguridad eléctrica."
    )

    secciones = {

        "Acceso al sistema": """
Ingrese con las credenciales autorizadas.
La información se almacena en la base de datos
asociada a la aplicación.

No comparta sus credenciales con otras personas.
        """,

        "01. Clientes": """
Registre los datos de la empresa para la cual
se desarrollará el proyecto.

Consulte los clientes existentes antes de crear
un nuevo registro. Utilice las opciones disponibles
para consultar, editar o eliminar información.
        """,

        "02. Proyectos": """
Seleccione un cliente y registre el proyecto
de seguridad eléctrica.

El código del proyecto permite identificar
y recuperar la información asociada.

Seleccione el proyecto correspondiente antes
de utilizar las herramientas técnicas.
        """,

        "03. Riesgos eléctricos": """
Cree una evaluación e incorpore los registros
de tareas y peligros correspondientes.

Documente las consecuencias, la valoración
inicial, las medidas de control y la valoración
residual.

Consulte la metodología incluida en el módulo.
        """,

        "04. Arco eléctrico y EPP": """
Registre las características del equipo,
el sistema eléctrico y los parámetros técnicos
disponibles.

El método de tablas solamente puede utilizarse
cuando se cumplen sus condiciones de aplicación.

Los resultados requieren validación profesional.
        """,

        "05. Etiquetas eléctricas": """
Seleccione los registros correspondientes
al proyecto.

Revise la información, prepare la vista previa
y utilice las opciones de almacenamiento
y exportación disponibles.

Las etiquetas académicas no deben utilizarse
directamente en instalaciones reales.
        """,

        "06. Bloqueo y etiquetado LOTO": """
Consulte los recursos de bloqueo y etiquetado.

Prepare la documentación correspondiente
al control de energías peligrosas y las
etiquetas asociadas.

La selección de dispositivos requiere comprobar
la compatibilidad con el equipo real.
        """,

        "07. Permisos de trabajo": """
Seleccione el tipo de permiso correspondiente.

Complete la información técnica, las medidas
de protección y las responsabilidades.

Los documentos generados son borradores
académicos y no autorizaciones de trabajo.
        """,

        "Almacenamiento y exportación": """
Utilice los botones de guardado antes de
abandonar un formulario.

Verifique el mensaje de confirmación.

Los documentos disponibles pueden exportarse
mediante las opciones de descarga de cada módulo.
        """,

        "Limitaciones de la aplicación": """
Electra Safe 360 es una herramienta académica.

No sustituye estudios eléctricos especializados,
evaluaciones realizadas por personal calificado
ni la revisión de la normativa aplicable.

No utilice datos reales o confidenciales durante
las actividades de demostración.
        """
    }

    for titulo, contenido in secciones.items():

        with st.expander(titulo):

            st.markdown(contenido)

    st.divider()

    st.caption(
        "Referencia normativa: NFPA 70E, edición 2027."
    )

    st.caption(
        "Tecnologías: Python, Streamlit, Supabase, "
        "GitHub y ReportLab."
    )

    st.caption(
        "Inteligencia artificial utilizada: ChatGPT."
    )
