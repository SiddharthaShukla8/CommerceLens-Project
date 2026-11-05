import streamlit as st

def kpi_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-help'>{help_text}</div></div>", unsafe_allow_html=True)

def inject_css() -> None:
    st.markdown("""<style>
    .stApp { background: #f6f8fc; } .block-container { padding-top: 2rem; max-width: 1400px; }
    .kpi { background: white; border: 1px solid #e6eaf2; border-radius: 12px; padding: 16px; min-height: 112px; box-shadow: 0 1px 3px #dce2ef55; }
    .kpi-label { color:#526176; font-size:.85rem; font-weight:600; }.kpi-value { color:#132b4f; font-size:1.7rem; font-weight:700; margin-top:6px; }.kpi-help {color:#7d8999;font-size:.72rem;margin-top:5px;}
    </style>""", unsafe_allow_html=True)
