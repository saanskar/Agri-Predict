"""
AgriPredict — Weather Analytics Page
======================================
Displays the weather data returned by the V1 backend for the last prediction.
Also renders a historical trend of all weather readings collected across
predictions made in this session (real values, no simulation).

If the user has not yet run a prediction, shows a prompt card.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from charts  import weather_sparkline
from utils   import irrigation_advice


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>🌤 Weather Analytics</h1>
        <p>Live weather conditions fetched for your location via Open-Meteo API</p>
    </div>
    """, unsafe_allow_html=True)

    weather = st.session_state.last_weather

    # ── Empty state ───────────────────────────────────────────────
    if not weather:
        st.markdown("""
        <div class="gc" style="text-align:center;padding:3.5rem 1rem">
            <div style="font-size:3.5rem;margin-bottom:0.9rem">🌦</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1.1rem;
                        color:#111827;margin-bottom:0.4rem">No weather data yet</div>
            <div style="font-size:0.86rem;color:#6B7280">
                Run a prediction on the <strong>Predict Crop</strong> page.
                Live weather is fetched automatically for your coordinates.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Parse real values ─────────────────────────────────────────
    temp = weather.get("temperature_c")
    hum  = weather.get("relative_humidity_pct")
    rain = weather.get("rainfall_mm", 0.0)

    def _fmt(v: Any, prec: int = 1) -> str:
        return f"{v:.{prec}f}" if v is not None else "—"

    # ── Current weather KPI cards ─────────────────────────────────
    st.markdown(f"""
    <div class="wg">
        <div class="wc">
            <div class="wc-ico">🌡️</div>
            <div class="wc-lbl">Temperature</div>
            <div class="wc-val">{_fmt(temp)}</div>
            <div class="wc-unit">°C</div>
        </div>
        <div class="wc">
            <div class="wc-ico">💧</div>
            <div class="wc-lbl">Rel. Humidity</div>
            <div class="wc-val">{_fmt(hum, 0)}</div>
            <div class="wc-unit">%</div>
        </div>
        <div class="wc">
            <div class="wc-ico">🌧️</div>
            <div class="wc-lbl">Rainfall</div>
            <div class="wc-val">{_fmt(rain)}</div>
            <div class="wc-unit">mm</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Session weather history trend ─────────────────────────────
    history = st.session_state.history
    if len(history) >= 2:
        # Build time-series from real prediction history (newest-first → reverse)
        ordered = list(reversed(history))
        labels  = [f"#{i+1}" for i in range(len(ordered))]
        temps   = [h["weather"].get("temperature_c", 0) for h in ordered]
        hums    = [h["weather"].get("relative_humidity_pct", 0) for h in ordered]

        st.markdown('<div class="gc"><div class="gc-title">📈 Weather Readings Across Predictions</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.74rem;color:#16A34A;margin-bottom:0.6rem">
            Real values from each prediction you have made this session.
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            weather_sparkline(temps, hums, labels),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown("</div>", unsafe_allow_html=True)

    elif len(history) == 1:
        st.markdown("""
        <div class="alert alert-info" style="font-size:0.82rem">
            📊 Make at least 2 predictions to see a weather trend chart.
        </div>
        """, unsafe_allow_html=True)

    # ── Irrigation advice ─────────────────────────────────────────
    rain_val = float(rain) if rain is not None else 0.0
    msg, level = irrigation_advice(rain_val)

    st.markdown(f"""
    <div class="gc">
        <div class="gc-title">🚿 Irrigation Recommendation</div>
        <div class="alert alert-{level}" style="margin-bottom:0.9rem">{msg}</div>
    """, unsafe_allow_html=True)

    # Detail breakdown
    def _row(icon: str, label: str, value: str, note: str, ok: bool) -> str:
        c = "#3ddc84" if ok else "#f5c842"
        e = "✅" if ok else "⚠️"
        return f"""
        <div style="display:flex;align-items:center;gap:0.8rem;
                    padding:0.55rem 0;border-bottom:1px solid rgba(61,220,132,0.07)">
            <span>{e}</span>
            <span style="font-size:0.85rem;font-weight:600;min-width:110px">{icon} {label}</span>
            <span style="font-size:0.82rem;color:{c}">{value} — {note}</span>
        </div>
        """

    temp_ok = temp is not None and 15 <= temp <= 35
    hum_ok  = hum  is not None and 40 <= hum  <= 80
    rain_ok = 5 <= rain_val <= 25

    st.markdown(
        _row("🌡️","Temperature", f"{_fmt(temp)}°C",
             "Optimal" if temp_ok else "Suboptimal for many crops", temp_ok) +
        _row("💧","Humidity",    f"{_fmt(hum, 0)}%",
             "Good range" if hum_ok else "May affect some crops", hum_ok) +
        _row("🌧️","Rainfall",    f"{_fmt(rain)} mm",
             "Adequate level" if rain_ok else "Monitor closely", rain_ok),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Source / location ─────────────────────────────────────────
    st.markdown(f"""
<div class="gc">
    <div class="gc-title">📍 Data Source</div>
    <div class="ir">
        <div class="ib"><div class="ib-l">Latitude</div>
            <div class="ib-v">{st.session_state.lat:.4f}°</div></div>
        <div class="ib"><div class="ib-l">Longitude</div>
            <div class="ib-v">{st.session_state.lon:.4f}°</div></div>
    </div>
</div>
""", unsafe_allow_html=True)
