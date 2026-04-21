"""
AgriPredict — Dashboard Page
==============================
Home screen: 5 live KPI cards, welcome card, soil gauge, quick stats,
and a "how it works" step-flow.

All displayed values come from st.session_state which is populated
after the user runs a prediction on the Predict page.
"""

from __future__ import annotations

import streamlit as st
from charts import confidence_bars, npk_bar, soil_gauge
from utils  import crop_emoji, crop_meta, soil_score


def render() -> None:
    # ── Page header ──────────────────────────────────────────────
    st.markdown("""
    <div class="ph">
        <h1>🌾 AgriPredict Dashboard</h1>
        <p>Enter your soil parameters and location to get AI-powered crop recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Gather state ──────────────────────────────────────────────
    result   = st.session_state.last_result
    weather  = st.session_state.last_weather or {}
    recs     = (result or {}).get("recommendations", [])
    top      = recs[0] if recs else None

    n  = float(st.session_state.n  or 90.0)
    p  = float(st.session_state.p  or 42.0)
    k  = float(st.session_state.k  or 43.0)
    ph = float(st.session_state.ph or 6.5)
    score = soil_score(n, p, k, ph)

    # live weather values
    def _fmt(v: Any, unit: str = "", fallback: str = "—") -> str:
        return f"{v:.1f}{unit}" if v is not None else fallback

    temp_s = _fmt(weather.get("temperature_c"),          "°C")
    hum_s  = _fmt(weather.get("relative_humidity_pct"),  "%")
    rain_s = _fmt(weather.get("rainfall_mm"),             " mm")

    crop_s = top["crop"].title()    if top else "Run Prediction"
    conf_s = f"{top['probability']*100:.1f}%" if top else "—"
    ico    = crop_emoji(top["crop"]) if top else "🌿"

    # ── KPI row ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-g">
        <div class="kpi" style="animation-delay:0s">
            <div class="kpi-ico">🌡️</div>
            <div class="kpi-lbl">Temperature</div>
            <div class="kpi-val">{temp_s}</div>
            <div class="kpi-sub">Live weather</div>
        </div>
        <div class="kpi" style="animation-delay:.05s">
            <div class="kpi-ico">💧</div>
            <div class="kpi-lbl">Humidity</div>
            <div class="kpi-val">{hum_s}</div>
            <div class="kpi-sub">Relative humidity</div>
        </div>
        <div class="kpi" style="animation-delay:.1s">
            <div class="kpi-ico">🌧️</div>
            <div class="kpi-lbl">Rainfall</div>
            <div class="kpi-val">{rain_s}</div>
            <div class="kpi-sub">Current reading</div>
        </div>
        <div class="kpi" style="animation-delay:.15s">
            <div class="kpi-ico">🧪</div>
            <div class="kpi-lbl">Soil Score</div>
            <div class="kpi-val">{score}/100</div>
            <div class="kpi-sub">Health index</div>
        </div>
        <div class="kpi" style="animation-delay:.2s">
            <div class="kpi-ico">{ico}</div>
            <div class="kpi-lbl">Best Crop</div>
            <div class="kpi-val" style="font-size:1.05rem">{crop_s}</div>
            <div class="kpi-sub">Top recommendation</div>
        </div>
        <div class="kpi" style="animation-delay:.25s">
            <div class="kpi-ico">🎯</div>
            <div class="kpi-lbl">Confidence</div>
            <div class="kpi-val">{conf_s}</div>
            <div class="kpi-sub">Model certainty</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column body ───────────────────────────────────────────
    l, r = st.columns([1.1, 1], gap="medium")

    with l:
        # Welcome / intro
        st.markdown("""
        <div class="gc">
            <div class="gc-title">🚀 Welcome to AgriPredict Pro</div>
            <p style="color:#374151;font-size:0.87rem;line-height:1.75;margin:0">
                An ensemble of <strong style="color:#3ddc84">Random Forest</strong>,
                <strong style="color:#3ddc84">XGBoost</strong>, and a
                <strong style="color:#3ddc84">Neural Network</strong> analyses your soil's
                N·P·K and pH together with live Open-Meteo weather data to recommend
                the crop most likely to thrive at your location.
            </p>
            <div style="margin-top:1.1rem;display:flex;gap:0.4rem;flex-wrap:wrap">
                <span class="tag">🤖 ML Ensemble</span>
                <span class="tag">🌦 Live Weather</span>
                <span class="tag">🧪 Soil Analysis</span>
                <span class="tag">📍 GPS Support</span>
                <span class="tag">📊 Charts</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Soil gauge
        st.markdown('<div class="gc"><div class="gc-title">🌱 Soil Health Overview</div>', unsafe_allow_html=True)
        st.plotly_chart(soil_gauge(score), use_container_width=True,
                        config={"displayModeBar": False})
        grade = (
            "Excellent 🌟" if score >= 80 else
            "Good 👍"      if score >= 60 else
            "Fair ⚠️"      if score >= 40 else
            "Poor 🔴"
        )
        st.markdown(f"""
        <div style="text-align:center;margin-top:-0.3rem">
            <div style="font-size:0.7rem;color:#16A34A">Current Rating</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1rem;color:#111827">{grade}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r:
        # Current soil + location
        st.markdown(f"""
        <div class="gc">
            <div class="gc-title">🧪 Current Soil Parameters</div>
            <div class="ir">
                <div class="ib"><div class="ib-l">Nitrogen N</div><div class="ib-v">{n:.0f} kg/ha</div></div>
                <div class="ib"><div class="ib-l">Phosphorus P</div><div class="ib-v">{p:.0f} kg/ha</div></div>
                <div class="ib"><div class="ib-l">Potassium K</div><div class="ib-v">{k:.0f} kg/ha</div></div>
                <div class="ib"><div class="ib-l">Soil pH</div><div class="ib-v">{ph:.1f}</div></div>
            </div>
            <div style="margin-top:0.9rem;padding-top:0.9rem;
                        border-top:1px solid rgba(61,220,132,0.1)">
                <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;
                            color:#16A34A;margin-bottom:0.3rem">LOCATION</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:#111827">
                    {f"{st.session_state.lat:.4f}°N" if st.session_state.lat is not None else "Not set"} &nbsp;/&nbsp; {f"{st.session_state.lon:.4f}°E" if st.session_state.lon is not None else "—"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Last prediction chart OR empty state
        if recs:
            st.markdown('<div class="gc"><div class="gc-title">📊 Latest Confidence Scores</div>', unsafe_allow_html=True)
            st.plotly_chart(confidence_bars(recs[:5]), use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="gc" style="text-align:center;padding:2.5rem 1rem">
                <div style="font-size:3rem;margin-bottom:0.7rem">🌱</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;color:#111827;margin-bottom:0.3rem">
                    No prediction yet
                </div>
                <div style="font-size:0.83rem;color:#6B7280">
                    Head to <strong>Predict Crop</strong> to get started
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────
    st.markdown("""
    <div class="gc" style="margin-top:0.2rem">
        <div class="gc-title">⚡ How It Works</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem">
            <div style="text-align:center;padding:0.6rem">
                <div style="font-size:1.9rem;margin-bottom:0.4rem">1️⃣</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:0.88rem;margin-bottom:0.25rem">Enter Soil Data</div>
                <div style="font-size:0.76rem;color:#6B7280">Input N, P, K values and soil pH from your lab report</div>
            </div>
            <div style="text-align:center;padding:0.6rem">
                <div style="font-size:1.9rem;margin-bottom:0.4rem">2️⃣</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:0.88rem;margin-bottom:0.25rem">Set Location</div>
                <div style="font-size:0.76rem;color:#6B7280">GPS coordinates or browser location button</div>
            </div>
            <div style="text-align:center;padding:0.6rem">
                <div style="font-size:1.9rem;margin-bottom:0.4rem">3️⃣</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:0.88rem;margin-bottom:0.25rem">AI Analysis</div>
                <div style="font-size:0.76rem;color:#6B7280">Live weather fetched + ML ensemble prediction runs</div>
            </div>
            <div style="text-align:center;padding:0.6rem">
                <div style="font-size:1.9rem;margin-bottom:0.4rem">4️⃣</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:0.88rem;margin-bottom:0.25rem">Get Results</div>
                <div style="font-size:0.76rem;color:#6B7280">Ranked crops with confidence, yield & profit info</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)