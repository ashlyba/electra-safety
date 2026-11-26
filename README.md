
# Electra Safe 360

## ElectraSafety Consultores

Sistema académico de apoyo a la evaluación,
documentación y gestión de la seguridad eléctrica.

Desarrollado con referencia a la NFPA 70E,
edición 2027.

## Funcionalidades

1. Administración de clientes.
2. Gestión de proyectos.
3. Evaluación de riesgos eléctricos.
4. Evaluación de arco eléctrico, EPP y fronteras.
5. Diseño y generación de etiquetas eléctricas.
6. Bloqueo y etiquetado LOTO.
7. Permisos de trabajo eléctrico.

## Arquitectura

- Interfaz de usuario: Streamlit.
- Lenguaje de programación: Python.
- Base de datos: Supabase.
- Autenticación: Supabase Auth.
- Generación de documentos: ReportLab.
- Control de versiones: GitHub.

## Inteligencia artificial

Se utilizó ChatGPT como herramienta de apoyo
durante el desarrollo, organización y documentación
del programa.

## Instalación local

Instalar las dependencias:

    pip install -r requirements.txt

Configurar las credenciales autorizadas de Supabase
en el archivo local:

    .streamlit/secrets.toml

Ejecutar:

    streamlit run app.py

## Almacenamiento

La información se organiza mediante clientes,
proyectos y registros técnicos asociados.

## Seguridad

No almacenar credenciales privadas en GitHub.

Utilizar únicamente cuentas autorizadas y datos
ficticios durante las demostraciones académicas.

## Referencia normativa

NFPA 70E, edición 2027.

## Limitaciones

La aplicación no sustituye la evaluación de
personal calificado ni los estudios eléctricos
especializados.

Los resultados técnicos y documentos requieren
revisión antes de cualquier utilización real.

## Versión

0.4 - Desarrollo académico.

Pendiente de validación integral y revisión
de los requisitos normativos.
