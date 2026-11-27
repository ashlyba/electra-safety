import streamlit as st


PAGINAS = {
    "Inicio y proyectos activos": (
        "Inicia sesión con la cuenta configurada para la aplicación. En Inicio encontrarás los siete módulos, el resumen general y el selector de proyectos.",
        "Selecciona el proyecto y verifica cliente, nombre y código en la barra lateral. El avance refleja cuántos módulos técnicos tienen registros.",
        "Usa Volver al panel principal para salir de una herramienta. Guarda los formularios antes de cambiar de módulo, proyecto o documento. Si aparece el aviso de navegación, puedes permanecer para guardar.",
    ),
    "01. Clientes": (
        "Registra el cliente y completa los campos que el formulario marca como obligatorios. En la consulta puedes buscar por empresa, identificación, correo o contacto.",
        "Selecciona el cliente para ver sus proyectos o editar sus datos. Revisa las relaciones antes de confirmar una eliminación. El listado filtrado se puede descargar en CSV o PDF.",
    ),
    "02. Proyectos": (
        "Crea el proyecto con un cliente existente, nombre, ubicación y datos de la intervención. El código se conserva al editar el proyecto.",
        "Desde la consulta puedes editar, duplicar o eliminar. La copia toma los datos generales y recibe un código nuevo. Los registros técnicos se mantienen vinculados al proyecto de origen.",
        "Para continuar, selecciona el proyecto en Inicio o en la herramienta técnica. Los módulos pueden utilizarse de forma independiente. El listado filtrado se descarga en CSV o PDF.",
    ),
    "03. Riesgos eléctricos": (
        "Crea una evaluación y registra cada par tarea–peligro. Describe el mecanismo de daño, las personas expuestas, las condiciones, los controles existentes y el posible error humano.",
        "Estima probabilidad y severidad entre 1 y 5 y justifica cada valoración. El sistema multiplica ambos valores para mostrar el riesgo inicial y el residual. Los umbrales de la matriz son académicos.",
        "Describe los controles en orden de jerarquía y fundamenta el tratamiento de los niveles superiores. Identifica a la persona responsable y el plazo. Registra evidencia si marcas los controles como verificados.",
        "En Consultar resultados puedes revisar, editar o eliminar peligros y descargar el PDF de la evaluación. El residual sin evidencia de verificación es una estimación condicionada.",
    ),
    "04. Arco eléctrico, choque y EPP": (
        "Abre Nueva evaluación. Completa equipo, tarea, condición, fuente y parámetros. Selecciona la fila de tarea aplicable y documenta la evidencia que respalda su elección.",
        "Para arco ingresa tensión nominal en V, corriente de falla disponible en kA, tiempo de despeje (CA) o duración del arco (CC) en s y distancia de trabajo en mm. Si coinciden ambas filas MCC, selecciona y justifica la fila aplicable.",
        "Para choque identifica si la parte expuesta es fija o móvil, la tensión de referencia y la elevación. En CA selecciona fase a fase, sistema monofásico o nota e cuando corresponda. Los límites de choque se muestran en m o con la indicación que figure en la tabla.",
        "Usa Evaluar parámetros y luego Guardar evaluación o Guardar nueva revisión si corresponde. Si faltan condiciones, el punto queda sin categoría tabulada. Se requiere revisión adicional para equipos resistentes al arco, CC fuera del alcance implementado y casos sin fila aplicable. La aplicación no calcula energía incidente, corriente de arco ni fronteras por fórmulas.",
        "En Consultar y editar puedes descargar el PDF. En Selección de EPP compara la clasificación del fabricante y los componentes con el mínimo tabulado. Registra por separado la protección dieléctrica. Abre, reevalúa y guarda puntos anteriores para reutilizarlos con los criterios actuales.",
    ),
    "05. Etiquetas para equipos": (
        "Desde evaluación recupera puntos vigentes del proyecto. Filtra por equipo, ubicación o categoría y selecciona un punto o un lote para vista previa, guardado e impresión.",
        "En Datos externos registra una categoría documentada por el método de tablas, la tensión nominal, la frontera de arco, la fuente, la revisión y la persona revisora.",
        "En Etiquetas guardadas consulta la vista previa. Si se actualiza o elimina el punto de origen, vuelve a generar la etiqueta. Las muestras se identifican como académicas.",
    ),
    "06. Bloqueo y etiquetado LOTO": (
        "En Catálogo de dispositivos puedes buscar por nombre, elegir dispositivos y descargar su ficha ilustrada. Confirma siempre el modelo y sus instrucciones.",
        "En Política y procedimiento crea un borrador por proyecto. Documenta funciones, fuentes, aislamiento, energía almacenada, verificación de ausencia de tensión, participantes, relevos y restitución. Registra aquí los dispositivos específicos adicionales.",
        "En Consultar y editar puedes continuar el borrador, iniciar la revisión y exportar el PDF. La pestaña Etiquetas LOTO permite diseñar, guardar y descargar muestras.",
    ),
    "07. Permisos": (
        "Selecciona Trabajo energizado o Trabajo desenergizado. Vincula las evaluaciones o el procedimiento LOTO del mismo proyecto cuando estén disponibles. Completa los campos técnicos pendientes y guarda el borrador.",
        "En el permiso energizado clasifica la necesidad con base en 130.3(A) y documenta la exención si corresponde. Separa choque, arco y sus medidas. Registra plan de seguridad, reunión previa, personal calificado y respuesta ante emergencias.",
        "En el permiso interno desenergizado identifica las fuentes, puntos de aislamiento, bloqueos y evidencia de verificación. Documenta la liberación y la restitución del escenario académico.",
        "En Consultar y editar selecciona el documento y registra cada acción documental con responsable, cargo, fundamento y confirmación. El sistema bloquea el avance si encuentra datos pendientes. Exporta el PDF con su estado y el historial.",
    ),
    "Referencias y alcance": (
        "NFPA 70E 2027, material del curso. Artículo 100 para definiciones, 110.3(H) e (I) para riesgos y planificación, artículo 120 para LOTO y condición de trabajo eléctricamente segura, y 130.2 a 130.7 para prácticas, permisos, choque, arco, etiquetado y EPP.",
        "Tablas 130.4(E)(a) y (b) para choques en CA y CC. Tabla 130.5(C)(3) para probabilidad de arco por tarea. Tablas 130.7(C)(15)(a), (b) y (c) para categorías y EPP. Los anexos F, G, H, I y J brindan orientación informativa.",
        "Los resultados sirven para el ejercicio universitario. La revisión documental de la aplicación corresponde al proyecto académico. Cualquier evaluación o autorización real exige revisión de una persona calificada y los procedimientos de la organización.",
    ),
}


def mostrar():
    st.title("Manual de uso")
    st.caption("Electra Safe 360 · ElectraSafety Consultores · Versión 1.1")
    tema = st.selectbox("Consultar", list(PAGINAS), key="tema_manual")
    st.subheader(tema)
    for instruccion in PAGINAS[tema]:
        st.write(instruccion)
