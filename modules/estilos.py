
import streamlit as st


def aplicar_estilos():

    st.html("""
    <style>

    :root {
        --azul: #0D2333;
        --amarillo: #FFB800;
        --fondo: #F2F5F8;
        --texto: #526779;
        --borde: #DFE6ED;
    }

    .stApp {
        background: var(--fondo);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2.5rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: var(--azul);
        font-size: 2.1rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.8px;
    }

    h2 {
        color: var(--azul);
        font-size: 1.55rem !important;
        font-weight: 700 !important;
    }

    h3 {
        color: var(--azul);
        font-weight: 650 !important;
    }

    /* MENU LATERAL */

    [data-testid="stSidebar"] {
        background: #0D2333;
        border-right: 1px solid #203A4C;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #E5EDF4;
    }

    [data-testid="stSidebar"] img {
        border-radius: 12px;
    }

    [data-testid="stSidebar"] hr {
        border-color: #304858;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 5px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 9px 10px;
        border-radius: 8px;
        transition: background 0.2s;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #203E50;
    }

    [data-testid="stSidebar"] label:has(
        input:checked
    ) {
        background: #294758;
        border-left: 3px solid #FFB800;
    }

    /* BOTONES */

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 43px;
        transition: all 0.18s ease;
    }

    button[kind="primary"] {
        background: #FFB800 !important;
        color: #0D2333 !important;
        border: 1px solid #FFB800 !important;
    }

    button[kind="primary"]:hover {
        background: #E9A700 !important;
        border-color: #E9A700 !important;
    }

    button[kind="secondary"] {
        border: 1px solid #D5DFE7;
    }

    button[kind="secondary"]:hover {
        border-color: #D49A00;
        color: #0D2333;
    }

    /* FORMULARIOS */

    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #DFE6ED;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 3px 12px #0D233306;
    }

    [data-testid="stWidgetLabel"] p {
        font-weight: 550;
        font-size: 0.91rem;
    }

    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="select"] > div {
        border-radius: 8px;
    }

    /* INDICADORES */

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DFE6ED;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 3px 10px #0D233307;
    }

    [data-testid="stMetricValue"] {
        font-weight: 700;
        color: #0D2333;
    }

    /* PESTAÑAS */

    [data-baseweb="tab-list"] {
        background: #FFFFFF;
        border: 1px solid #DFE6ED;
        border-radius: 10px;
        padding: 5px;
        gap: 8px;
    }

    [data-baseweb="tab"] {
        padding: 12px 18px;
        font-weight: 600;
    }

    /* CONTENEDORES */

    [data-testid="stExpander"] {
        background: #FFFFFF;
        border-radius: 10px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ENCABEZADO PRINCIPAL */

    .banner {
        background: linear-gradient(
            120deg,
            #0D2333,
            #173B50
        );
        border-left: 6px solid #FFB800;
        padding: 32px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    .banner-titulo {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #FFFFFF !important;
        margin-bottom: 10px;
    }

    .banner-subtitulo {
        color: #D4E0E9 !important;
        font-size: 16px;
        line-height: 1.6;
    }

    .banner-norma {
        color: #FFB800 !important;
        font-size: 13px;
        font-weight: 650;
        margin-top: 20px;
        letter-spacing: 0.8px;
    }

    /* TARJETAS DE HERRAMIENTAS */

    .modulo {
        background: #FFFFFF;
        border: 1px solid #DFE6ED;
        border-top: 4px solid #FFB800;
        border-radius: 14px;
        padding: 23px;
        min-height: 185px;
        margin-top: 8px;
        box-shadow: 0 4px 12px #0D233308;
        transition: all 0.2s ease;
    }

    .modulo:hover {
        box-shadow: 0 8px 22px #0D233312;
        transform: translateY(-2px);
    }

    .modulo-titulo {
        color: #0D2333;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .modulo p {
        color: #526779;
        font-size: 14px;
        line-height: 1.6;
    }

    .estado-activo {
        color: #526779;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        margin-top: 15px;
    }

    /* PIE DE PAGINA */

    .pie {
        text-align: center;
        font-size: 12px;
        color: #64748B;
        padding: 25px;
        margin-top: 30px;
        border-top: 1px solid #DFE6ED;
    }

    @media (max-width: 768px) {

        .block-container {
            padding: 1.5rem 1rem;
        }

        .banner {
            padding: 22px;
        }

        .banner-titulo {
            font-size: 28px;
        }

        h1 {
            font-size: 1.65rem !important;
        }

        [data-testid="stForm"] {
            padding: 15px;
        }

    }

    </style>
    """)
