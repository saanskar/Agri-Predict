"""
AgriPredict — Soil Health Page
================================
Detailed breakdown of the user's current NPK and pH values.
Uses real session_state inputs — no fake data.
Allows the user to update values and see impacts immediately.
"""

from __future__ import annotations

import streamlit as st

from charts import npk_bar, ph_scale_html, soil_gauge
from utils  import soil_score, soil_tips


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>🧪 Soil Health Analysis</h1>
        <p>Detailed NPK status, pH assessment, and fertiliser recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    n  = float(st.session_state.n)
    p  = float(st.session_state.p)
    k  = float(st.session_state.k)
    ph = float(st.session_state.ph)
    score = soil_score(n, p, k, ph)

    # ── Top row: gauge + pH ───────────────────────────────────────
    g_col, ph_col = st.columns([1, 1.3], gap="medium")

    with g_col:
        st.markdown('<div class="gc"><div class="gc-title">🌱 Overall Soil Score</div>', unsafe_allow_html=True)
        st.plotly_chart(soil_gauge(score), use_container_width=True,
                        config={"displayModeBar": False})
        grade = (
            "Excellent 🌟" if score >= 80 else
            "Good 👍"      if score >= 60 else
            "Fair ⚠️"      if score >= 40 else
            "Poor 🔴"
        )
        st.markdown(f"""
        <div style="text-align:center;margin-top:-0.4rem">
            <div style="font-size:0.62rem;color:#16A34A">RATING</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1rem;color:#fff">{grade}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with ph_col:
        st.markdown('<div class="gc"><div class="gc-title">🔬 Soil pH</div>', unsafe_allow_html=True)
        st.markdown(ph_scale_html(ph), unsafe_allow_html=True)

        if ph < 5.0:
            ph_note, ph_cls = "Very acidic — significantly limits nutrient uptake", "danger"
        elif ph < 5.5:
            ph_note, ph_cls = "Acidic — some crops may struggle", "warn"
        elif ph < 6.0:
            ph_note, ph_cls = "Mildly acidic — suitable for acid-loving crops", "ok"
        elif ph <= 7.0:
            ph_note, ph_cls = "Neutral — optimal for most crops ✅", "ok"
        elif ph <= 7.5:
            ph_note, ph_cls = "Mildly alkaline — tolerated by most crops", "ok"
        elif ph <= 8.0:
            ph_note, ph_cls = "Alkaline — can limit micronutrient availability", "warn"
        else:
            ph_note, ph_cls = "Highly alkaline — serious nutrient deficiency risk", "danger"

        st.markdown(f'<div class="alert alert-{ph_cls}" style="margin-top:0.8rem">{ph_note}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── NPK bar chart ─────────────────────────────────────────────
    st.markdown('<div class="gc"><div class="gc-title">📊 NPK vs Ideal Levels</div>', unsafe_allow_html=True)
    st.plotly_chart(npk_bar(n, p, k), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Nutrient detail rows ──────────────────────────────────────
    st.markdown('<div class="gc"><div class="gc-title">🌿 Nutrient Status Detail</div>', unsafe_allow_html=True)

    def _status(val: float, lo: float, hi: float) -> tuple[str, str]:
        if val < lo * 0.4:   return "Deficient", "#f55a5a"
        if val < lo:         return "Low",        "#f5c842"
        if val <= hi:        return "Adequate",   "#3ddc84"
        if val <= hi * 1.5:  return "High",       "#f5c842"
        return "Excess", "#f55a5a"

    _nutrients = [
        ("🟢 Nitrogen (N)",   n,  300, "#3ddc84", 40, 120,
         "Promotes leaf & stem growth · essential for photosynthesis"),
        ("🟡 Phosphorus (P)", p,  300, "#f5c842", 30, 100,
         "Root development & energy transfer · key for flowering"),
        ("🔵 Potassium (K)",  k,  300, "#5ad8ff", 30, 100,
         "Disease resistance · water regulation · fruit quality"),
    ]
    for name, val, cap, colour, lo, hi, desc in _nutrients:
        pct = min(100, round(val / cap * 100))
        stat, stat_c = _status(val, lo, hi)
        st.markdown(f"""
        <div class="nr">
            <div class="nr-name">{name}</div>
            <div class="nr-bar">
                <div class="nr-bg">
                    <div class="nr-fill" style="width:{pct}%;background:{colour}"></div>
                </div>
                <div style="font-size:0.63rem;color:#9CA3AF;margin-top:2px">{desc}</div>
            </div>
            <div class="nr-val">{val:.0f} kg/ha</div>
            <div class="nr-tag" style="color:{stat_c}">{stat}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Suggestions ───────────────────────────────────────────────
    st.markdown('<div class="gc"><div class="gc-title">💡 Fertiliser & Amendment Recommendations</div>',
                unsafe_allow_html=True)
    for text, level in soil_tips(n, p, k, ph):
        st.markdown(f'<div class="alert alert-{level}">{text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Update values ─────────────────────────────────────────────
    with st.expander("✏️ Update Soil Values", expanded=False):
        u1, u2, u3, u4 = st.columns(4)
        with u1: new_n  = st.number_input("N (kg/ha)", 0.0, 300.0, n,  1.0, key="upd_n")
        with u2: new_p  = st.number_input("P (kg/ha)", 0.0, 300.0, p,  1.0, key="upd_p")
        with u3: new_k  = st.number_input("K (kg/ha)", 0.0, 300.0, k,  1.0, key="upd_k")
        with u4: new_ph = st.number_input("pH",        0.0,  14.0, ph, 0.1, key="upd_ph")

        if st.button("💾 Save & Update", key="save_soil"):
            st.session_state.update(n=new_n, p=new_p, k=new_k, ph=new_ph)
            # Clear last result so dashboard reflects updated params
            st.session_state.last_result = None
            st.session_state.last_weather = None
            st.success("✅ Soil values updated! Run a new prediction to see recommendations.")
            st.rerun()
