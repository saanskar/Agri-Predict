"""
AgriPredict Merged — app.py
============================
Main entry point. Run with:  streamlit run app.py
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

NAV_ITEMS = {
    "🏠 Dashboard":         "dashboard",
    "🌱 Predict Crop":      "predict",
    "🌤 Weather Analytics": "weather",
    "🧪 Soil Health":       "soil",
    "📋 History":           "history",
    "📖 About":             "about",
}

# ── Mobile top navigation (shown only on small screens via CSS) ───────────────
st.markdown('<div class="mobile-nav">', unsafe_allow_html=True)
mobile_page = st.selectbox(
    "Navigate",
    list(NAV_ITEMS.keys()),
    key="mobile_nav_select",
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

    page_label = st.radio(
        "Navigation",
        list(NAV_ITEMS.keys()),
        key="sidebar_nav",
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#F3F4F6;margin:0.9rem 0 0.6rem'/>",
                unsafe_allow_html=True)
    with st.spinner("Checking API…"):
        api_ok = check_api_health()

    dot        = "🟢" if api_ok else "🔴"
    badge_lbl  = "Online" if api_ok else "Starting…"
    badge_col  = "#15803D" if api_ok else "#D97706"
    badge_hint = "" if api_ok else "<br><span style='font-size:0.7rem;color:#9CA3AF'>Cold start ~30 s</span>"
    st.markdown(f"""
    <div style="padding:0.6rem 0.85rem;background:#F8FAFC;
                border:1px solid #E5E7EB;border-radius:10px;
                font-size:0.8rem;color:#374151">
        {dot} Backend: <strong style="color:{badge_col}">{badge_lbl}</strong>{badge_hint}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:1rem 0 0.5rem;font-size:0.66rem;color:#D1D5DB;text-align:center">
        AgriPredict · v2.0
    </div>
    """, unsafe_allow_html=True)

# ── Resolve active page: mobile selectbox wins on mobile, sidebar on desktop ──
# Both controls update session state; we check screen width via CSS class trick.
# Simpler: just sync — whichever changed last wins. We use sidebar on desktop,
# mobile selectbox on mobile. Since both are rendered, we pick mobile_nav_select
# when sidebar default hasn't changed from session init, otherwise sidebar.
import streamlit.components.v1 as _components

# Determine active page key
page_key = NAV_ITEMS.get(mobile_page, "dashboard")
# Sidebar radio overrides when user explicitly clicks it
if "sidebar_nav" in st.session_state:
    page_key = NAV_ITEMS.get(st.session_state["sidebar_nav"], page_key)

_PAGES = {
    "dashboard": dashboard,
    "predict":   predict,
    "weather":   weather,
    "soil":      soil,
    "history":   history,
    "about":     about,
}
_PAGES[page_key].render()
