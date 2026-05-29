"""
app.py — Al-Qurnayn Field Platform
Entry point: shows login screen, then redirects to Home Dashboard.
Run:  streamlit run app.py
"""
import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from config import PLATFORM_NAME, PLATFORM_SUBTITLE, VERSION, GLOBAL_CSS
from auth import require_auth

st.set_page_config(
    page_title=f"{PLATFORM_NAME} — Login",
    page_icon="🛢️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject fonts + base CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── If already authenticated → jump straight to Home Dashboard ────────────────
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Home_Dashboard.py")

# ── Otherwise show login ──────────────────────────────────────────────────────
from auth import _render_login
_render_login()
