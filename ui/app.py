"""
AgriPredict Merged — app.py
============================
Single session_state key drives all navigation.
Both mobile dropdown and desktop sidebar update the same key.
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="AgriPredict Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

import styles
from utils import check_api_health, init_session
from pages import dashboard, predict, weather, soil, history, about

styles.inject()
init_session(st)

# ── Navigation items ──────────────────────────────────────────────────────────
NAV_LABELS = [
    "🏠 Dashboard",
    "🌱 Predict Crop",
    "🌤 Weather Analytics",
    "🧪 Soil Health",
    "📋 History",
    "📖 About",
]
NAV_MAP = {
    "🏠 Dashboard":         "dashboard",
    "🌱 Predict Crop":      "predict",
    "🌤 Weather Analytics": "weather",
    "🧪 Soil Health":       "soil",
    "📋 History":           "history",
    "📖 About":             "about",
}

# Initialise the single routing key
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Dashboard"


# ── Callback functions ────────────────────────────────────────────────────────
def _on_mobile_change():
    st.session_state.active_page = st.session_state._mobile_sel

def _on_sidebar_change():
    st.session_state.active_page = st.session_state._sidebar_sel


# ── Mobile top dropdown (hidden on desktop via CSS) ───────────────────────────
st.markdown('<div class="mobile-nav">', unsafe_allow_html=True)
st.selectbox(
    "Navigate",
    NAV_LABELS,
    index=NAV_LABELS.index(st.session_state.active_page),
    key="_mobile_sel",
    on_change=_on_mobile_change,
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sl">
        <div class="sl-title">🌾 AgriPredict</div>
        <div class="sl-sub">AI PRECISION AGRICULTURE</div>
    </div>
    """, unsafe_allow_html=True)

    st.radio(
        "Navigation",
        NAV_LABELS,
        index=NAV_LABELS.index(st.session_state.active_page),
        key="_sidebar_sel",
        on_change=_on_sidebar_change,
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#F3F4F6;margin:0.9rem 0 0.6rem'/>",
                unsafe_allow_html=True)

    with st.spinner("Checking model…"):
        api_ok = check_api_health()

    dot        = "🟢" if api_ok else "🔴"
    badge_lbl  = "Model Ready ✅" if api_ok else "Loading…"
    badge_col  = "#15803D" if api_ok else "#D97706"
    badge_hint = "" if api_ok else "<br><span style='font-size:0.7rem;color:#9CA3AF'>Model files missing</span>"
    st.markdown(f"""
    <div style="padding:0.6rem 0.85rem;background:#F8FAFC;
                border:1px solid #E5E7EB;border-radius:10px;
                font-size:0.8rem;color:#374151">
        {dot} Status: <strong style="color:{badge_col}">{badge_lbl}</strong>{badge_hint}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:1rem 0 0.5rem;font-size:0.66rem;color:#D1D5DB;text-align:center">
        AgriPredict · v2.0
    </div>
    """, unsafe_allow_html=True)


# ── Route to active page ──────────────────────────────────────────────────────
_PAGES = {
    "dashboard": dashboard,
    "predict":   predict,
    "weather":   weather,
    "soil":      soil,
    "history":   history,
    "about":     about,
}

page_key = NAV_MAP[st.session_state.active_page]
_PAGES[page_key].render()