# Electra Safe 360

## ElectraSafety Consultores

Maletín digital académico para la gestión
de seguridad eléctrica.

Referencia normativa: NFPA 70E, edición 2027.

## Módulos

1. Administración de clientes.
2. Gestión de proyectos.
3. Evaluación de riesgos eléctricos.
4. Arco eléctrico, EPP y fronteras.
5. Etiquetas eléctricas.
6. Bloqueo y etiquetado LOTO.
7. Permisos de trabajo.

## Tecnologías

- Python
- Streamlit
- Supabase
- ReportLab
- Pandas
- GitHub

## Inteligencia artificial

ChatGPT se utilizó como herramienta de apoyo
durante la programación, diseño, organización
y documentación del sistema.

## Instalación

Instalar las dependencias:

    pip install -r requirements.txt

Configurar las credenciales autorizadas
de Supabase mediante:

    .streamlit/secrets.toml

Ejecutar la aplicación:

    streamlit run app.py

## Archivo de entrada

app.py

## Almacenamiento

Los registros se almacenan en Supabase
y se organizan por cliente y proyecto.

## Seguridad

Las credenciales no deben publicarse
en el repositorio.

Utilizar datos ficticios para demostraciones.

## Limitaciones

Herramienta académica de apoyo.

No sustituye estudios eléctricos especializados,
la consulta de la normativa ni la revisión
por personal calificado.

Los documentos generados no constituyen
autorizaciones reales de trabajo.

## Versión

1.1. Revisión académica del código y de las tablas proporcionadas en el curso.
La conexión, las políticas de acceso y la persistencia deben comprobarse en el
proyecto Supabase utilizado para la demostración.

El archivo `.streamlit/secrets.toml` debe definir `[supabase]` con
`url` y `key`. Utilice la clave pública del proyecto (publishable o anon)
y autentique a cada usuario. Mantenga las políticas de acceso en el servidor.
La aplicación espera las tablas y los códigos automáticos del proyecto Supabase.
