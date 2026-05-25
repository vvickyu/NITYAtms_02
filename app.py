"""
Nitya VFX Studio — Production Portal
Serves the exact HTML interface with auto-save via localStorage
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Nitya VFX Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide ALL Streamlit chrome so only your HTML shows
st.markdown("""
<style>
#MainMenu, header, footer, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
.stApp { overflow: hidden; }
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
iframe { border: none !important; display: block; }
</style>
""", unsafe_allow_html=True)

# Load the portal HTML
html_path = os.path.join(os.path.dirname(__file__), "portal.html")

try:
    with open(html_path, "r", encoding="utf-8") as f:
        portal_html = f.read()
except FileNotFoundError:
    st.error("portal.html not found. Make sure it is in the same folder as app.py")
    st.stop()

# Render at full viewport height — exact same UI, no Streamlit wrapping
st.components.v1.html(
    portal_html,
    height=1000,
    scrolling=True
)
