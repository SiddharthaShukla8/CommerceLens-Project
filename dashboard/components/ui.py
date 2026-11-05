import streamlit as st

def kpi_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-help'>{help_text}</div></div>", unsafe_allow_html=True)

def inject_css() -> None:
    st.markdown("""<style>
    :root {
      --cl-navy: #0f2747;
      --cl-ink: #172033;
      --cl-muted: #52637a;
      --cl-border: #d8e1ee;
      --cl-surface: #ffffff;
      --cl-canvas: #f5f7fb;
      --cl-sidebar: #101a2b;
      --cl-accent: #2563eb;
      --cl-accent-hover: #1d4ed8;
      --cl-info-bg: #e0f2fe;
      --cl-info-text: #0c4a6e;
    }

    .stApp { background: var(--cl-canvas); color: var(--cl-ink); }
    .block-container { max-width: 1400px; padding-top: 2.25rem; padding-bottom: 3rem; }
    .stApp h1, .stApp h2, .stApp h3 { color: var(--cl-navy); letter-spacing: -0.02em; }
    .stApp h1 { font-weight: 750; }
    .stApp p, .stApp li, .stApp [data-testid="stMarkdownContainer"] { color: var(--cl-ink); }

    /* Sidebar has its own dark surface, so never inherit main-page text colours. */
    [data-testid="stSidebar"] { background: var(--cl-sidebar); border-right: 1px solid #243247; }
    [data-testid="stSidebar"] * { color: #e5edf8; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] small { color: #b8c5d8 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] label { color: #d9e4f4 !important; font-weight: 600; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #e5edf8 !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { color: #ffffff !important; }
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] { color: #e5edf8; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {
      background: #18263a !important;
      border-color: #40536d !important;
      color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] input { color: #f8fafc !important; }

    /* Keep interactive controls readable on the light content surface. */
    [data-testid="stMain"] [data-baseweb="select"] > div,
    [data-testid="stMain"] [data-baseweb="input"] > div,
    [data-testid="stMain"] input {
      background: #ffffff;
      border-color: #b9c7da;
      color: var(--cl-ink);
    }
    [data-testid="stMain"] [data-baseweb="select"] span,
    [data-testid="stMain"] [data-baseweb="input"] input { color: var(--cl-ink) !important; }
    [data-testid="stMain"] button[kind="primary"] { background: var(--cl-accent); border-color: var(--cl-accent); }
    [data-testid="stMain"] button[kind="primary"]:hover { background: var(--cl-accent-hover); border-color: var(--cl-accent-hover); }

    .kpi {
      background: var(--cl-surface);
      border: 1px solid var(--cl-border);
      border-radius: 14px;
      box-shadow: 0 4px 12px rgba(15, 39, 71, 0.07);
      min-height: 118px;
      padding: 18px;
    }
    .kpi-label { color: #42546d; font-size: .87rem; font-weight: 700; }
    .kpi-value { color: var(--cl-navy); font-size: 1.75rem; font-weight: 750; margin-top: 7px; }
    .kpi-help { color: #5f6f84; font-size: .76rem; margin-top: 6px; }

    /* Insight callouts need a light, high-contrast treatment. */
    [data-testid="stMain"] [data-testid="stAlert"] {
      background: var(--cl-info-bg);
      border: 1px solid #7dd3fc;
      border-radius: 10px;
      color: var(--cl-info-text);
    }
    [data-testid="stMain"] [data-testid="stAlert"] *,
    [data-testid="stMain"] [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
      color: var(--cl-info-text) !important;
    }

    [data-testid="stMetric"] {
      background: var(--cl-surface);
      border: 1px solid var(--cl-border);
      border-radius: 14px;
      padding: 14px 16px;
      box-shadow: 0 4px 12px rgba(15, 39, 71, 0.05);
    }
    [data-testid="stMetricLabel"] p { color: #42546d !important; font-weight: 700; }
    [data-testid="stMetricValue"] { color: var(--cl-navy) !important; }
    </style>""", unsafe_allow_html=True)
