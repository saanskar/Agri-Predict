"""
AgriPredict Merged — app.py
============================
Main entry point. Run with:  streamlit run app.py

Architecture
─────────────
• This file owns the sidebar navigation, global CSS injection,
  session-state initialisation, and API health indicator.
• Each page is a module in pages/ with a single render() function.
• The V1 FastAPI backend is used unchanged — all prediction logic
  lives server-side at AGRIPREDICT_API_BASE_URL.
• The V1 browser geolocation component (components/) is imported
  inside pages/predict.py — it is never called from this file.
"""

from __future__ import annotations

import streamlit as st

# ── Streamlit page config (must be the very first st call) ────────────────────
st.set_page_config(
    page_title="AgriPredict Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports (after set_page_config) ──────────────────────────────────
import styles
from utils import check_api_health, init_session

# ── Page modules ──────────────────────────────────────────────────────────────
from pages import dashboard, predict, weather, soil, history, about

# ── Bootstrap ─────────────────────────────────────────────────────────────────
styles.inject()
init_session(st)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / brand
    st.markdown("""
    <div class="sl">
        <div class="sl-title">🌾 AgriPredict</div>
        <div class="sl-sub">AI PRECISION AGRICULTURE</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    NAV_ITEMS = {
        "🏠 Dashboard":         "dashboard",
        "🌱 Predict Crop":      "predict",
        "🌤 Weather Analytics": "weather",
        "🧪 Soil Health":       "soil",
        "📋 History":           "history",
        "📖 About":             "about",
    }
    page_label = st.radio(
        "Navigation",
        list(NAV_ITEMS.keys()),
        label_visibility="collapsed",
    )
    page_key = NAV_ITEMS[page_label]

    # API status badge
    st.markdown("<hr style='border-color:#F3F4F6;margin:0.9rem 0 0.6rem'/>",
                unsafe_allow_html=True)
    with st.spinner("Checking API…"):
        api_ok = check_api_health()

    dot       = "🟢" if api_ok else "🔴"
    badge_lbl = "Online" if api_ok else "Starting…"
    badge_col = "#15803D" if api_ok else "#D97706"
    badge_hint = "" if api_ok else "<br><span style='font-size:0.7rem;color:#9CA3AF'>Cold start ~30 s</span>"
    st.markdown(f"""
    <div style="padding:0.6rem 0.85rem;background:#F8FAFC;
                border:1px solid #E5E7EB;border-radius:10px;
                font-size:0.8rem;color:#374151">
        {dot} Backend: <strong style="color:{badge_col}">{badge_lbl}</strong>{badge_hint}
    </div>
    """, unsafe_allow_html=True)

    # Minimal footer
    st.markdown("""
    <div style="padding:1rem 0 0.5rem;font-size:0.66rem;color:#D1D5DB;text-align:center">
        AgriPredict  ·  v2.0
    </div>
    """, unsafe_allow_html=True)

# ── Route to selected page ─────────────────────────────────────────────────────
_PAGES = {
    "dashboard": dashboard,
    "predict":   predict,
    "weather":   weather,
    "soil":      soil,
    "history":   history,
    "about":     about,
}
_PAGES[page_key].render()
