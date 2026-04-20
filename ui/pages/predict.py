"""
AgriPredict — Predict Crop Page
=================================
The core prediction page.

Flow:
  1. User fills soil N/P/K/pH and location inputs.
  2. Browser geolocation (V1 component) can auto-fill lat/lon.
  3. On submit → POST to V1 FastAPI backend.
  4. Response populates session state → results render in-page.

All result values come exclusively from the real API response.
"""

from __future__ import annotations

from typing import Any

import httpx
import streamlit as st

from charts  import confidence_bars, crop_radar, npk_bar
from utils   import (
    APIError, NetworkError,
    call_recommendations, crop_emoji, crop_meta,
    irrigation_advice, push_history,
)

try:
    from components.geolocation import get_browser_location
    _GEO_OK = True
except Exception:
    _GEO_OK = False
    def get_browser_location(**_: Any) -> dict[str, Any]:  # type: ignore[misc]
        return {"error": "Geolocation component not available."}


# ─────────────────────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>🌱 Predict Optimal Crop</h1>
        <p>Enter your soil parameters and location — the AI ensemble does the rest</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout: form | live preview ────────────────────
    form_col, prev_col = st.columns([1.2, 1], gap="medium")

    # ── SOIL PARAMETERS ───────────────────────────────────────────
    with form_col:
        st.markdown('<div class="gc"><div class="gc-title">🧪 Soil Parameters</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            n  = st.number_input("Nitrogen (N) kg/ha",   0.0, 300.0,
                                 float(st.session_state.n),  1.0, key="inp_n")
            k  = st.number_input("Potassium (K) kg/ha",  0.0, 300.0,
                                 float(st.session_state.k),  1.0, key="inp_k")
        with c2:
            p  = st.number_input("Phosphorus (P) kg/ha", 0.0, 300.0,
                                 float(st.session_state.p),  1.0, key="inp_p")
            ph = st.number_input("Soil pH",              0.0,  14.0,
                                 float(st.session_state.ph), 0.1, key="inp_ph")
        # Live mini-grid
        st.markdown(f"""
        <div class="ir" style="margin-top:0.75rem">
            <div class="ib"><div class="ib-l">N</div><div class="ib-v">{n:.0f}</div></div>
            <div class="ib"><div class="ib-l">P</div><div class="ib-v">{p:.0f}</div></div>
            <div class="ib"><div class="ib-l">K</div><div class="ib-v">{k:.0f}</div></div>
            <div class="ib"><div class="ib-l">pH</div><div class="ib-v">{ph:.1f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── LOCATION ──────────────────────────────────────────────
        st.markdown('<div class="gc"><div class="gc-title">📍 Location</div>', unsafe_allow_html=True)
        if _GEO_OK:
            if st.button("📡 Use My Browser Location", key="geo_btn"):
                st.session_state.request_geo = True
            if st.session_state.get("request_geo"):
                loc = get_browser_location(timeout_ms=12_000, key="geo_predict")
                if isinstance(loc, dict):
                    if "lat" in loc and "lon" in loc:
                        st.session_state.lat = float(loc["lat"])
                        st.session_state.lon = float(loc["lon"])
                        st.session_state.request_geo = False
                        st.success(f"✅ Location updated: {loc['lat']:.4f}°, {loc['lon']:.4f}°")
                    elif "error" in loc:
                        st.session_state.request_geo = False
                        st.error(f"Could not get location: {loc['error']}")
                    else:
                        # Still waiting
                        st.info("📡 Waiting for browser location… (click Allow if prompted)")
        else:
            st.markdown("""
            <div class="alert alert-info" style="font-size:0.8rem;margin-bottom:0.6rem">
                📍 Browser geolocation component not available — enter coordinates manually.
            </div>
            """, unsafe_allow_html=True)

        gc1, gc2 = st.columns(2)
        with gc1:
            _lat = st.number_input("Latitude",  -90.0,  90.0, step=0.001, key="lat")
        with gc2:
            _lon = st.number_input("Longitude",-180.0, 180.0, step=0.001, key="lon")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── SETTINGS ──────────────────────────────────────────────
        st.markdown('<div class="gc"><div class="gc-title">⚙️ Settings</div>', unsafe_allow_html=True)
        top_k = st.slider("Crops to recommend", 1, 10, int(st.session_state.top_k), key="top_k")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── SUBMIT ────────────────────────────────────────────────
        submitted = st.button("🌾 Get Crop Recommendations", type="primary", key="submit")

    # ── LIVE PREVIEW COLUMN ───────────────────────────────────────
    with prev_col:
        st.markdown('<div class="gc"><div class="gc-title">📊 NPK Live Preview</div>', unsafe_allow_html=True)
        st.plotly_chart(npk_bar(n, p, k), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="gc">
            <div class="gc-title">💡 Input Reference</div>
            <div style="font-size:0.82rem;color:#374151;line-height:1.9">
                <strong style="color:#16A34A">N</strong> — 40–120 kg/ha ideal<br>
                <strong style="color:#16A34A">P</strong> — 30–100 kg/ha ideal<br>
                <strong style="color:#16A34A">K</strong> — 30–100 kg/ha ideal<br>
                <strong style="color:#16A34A">pH</strong> — 5.5–7.5 for most crops<br>
                <br>
                <span style="color:#9CA3AF;font-size:0.76rem">
                Get NPK values from a certified soil testing lab or a rapid soil test kit.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── API CALL ──────────────────────────────────────────────────
    if submitted:
        # Persist inputs to session state
        st.session_state.update(n=n, p=p, k=k, ph=ph)

        with st.spinner("🔄 Fetching live weather · Running ML ensemble…"):
            try:
                data = call_recommendations(
                    float(_lat), float(_lon), n, p, k, ph, top_k
                )
                st.session_state.api_error   = None
                st.session_state.last_result = data
                st.session_state.last_weather = data.get("weather", {})
                push_history(st, n, p, k, ph, float(_lat), float(_lon),
                             data.get("recommendations", []),
                             data.get("weather", {}))

            except APIError as exc:
                st.session_state.api_error = str(exc)
                st.error(f"⚠️ Backend error {exc.status}: {exc.detail}")
                _show_error_help(exc.status)
                return

            except NetworkError as exc:
                st.session_state.api_error = str(exc)
                st.error(f"⚠️ Network error: {exc}")
                st.markdown("""
                <div class="alert alert-warn">
                  The backend may be starting up (cold start ~30 s on free tier).
                  Wait a moment and try again.
                </div>
                """, unsafe_allow_html=True)
                return

        st.success("✅ Analysis complete!")

    # ── RESULTS ───────────────────────────────────────────────────
    result = st.session_state.last_result
    if not result:
        return

    recs    = result.get("recommendations", [])
    weather = st.session_state.last_weather or {}

    if not recs:
        st.warning("The API returned an empty recommendation list.")
        return

    st.markdown("---")
    if not submitted:
        st.markdown("""
        <div style="color:#16A34A;font-size:0.78rem;margin-bottom:0.5rem">
            📋 Showing last prediction — submit the form to refresh
        </div>
        """, unsafe_allow_html=True)

    _render_results(recs, weather)


# ── Result rendering ──────────────────────────────────────────────────────────

def _render_results(recs: list[dict[str, Any]], weather: dict[str, Any]) -> None:
    top  = recs[0]
    meta = crop_meta(top["crop"])
    conf = float(top["probability"]) * 100

    suitability = (
        "Excellent Match ✨" if conf > 70 else
        "Good Match 👍"     if conf > 40 else
        "Possible Match ⚠️"
    )

    # ── Main banner ───────────────────────────────────────────────
    st.markdown(f"""
    <div class="mrb">
        <span class="mrb-ico">{meta['emoji']}</span>
        <div class="mrb-crop">{top['crop'].title()}</div>
        <div class="mrb-conf">Confidence: {conf:.1f}%</div>
        <div class="mrb-tags">
            <span class="tag">🎯 {suitability}</span>
            <span class="tag">💧 Water: {meta['water']}</span>
            <span class="tag">📦 Yield: {meta['yield']}</span>
            <span class="tag">💰 Profit: {meta['profit']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two cols: ranked list | charts ────────────────────────────
    rl, rr = st.columns([1.1, 1], gap="medium")

    with rl:
        st.markdown('<div class="gc"><div class="gc-title">🏆 Top Recommendations</div>', unsafe_allow_html=True)
        max_prob = max(float(r["probability"]) for r in recs) or 1.0
        for i, rec in enumerate(recs, 1):
            c    = rec["crop"]
            prob = float(rec["probability"])
            pct  = prob * 100
            bar  = max(3, round(prob / max_prob * 100))
            m    = crop_meta(c)
            icon = ("🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}")
            cls  = " r1" if i == 1 else ""
            delay = f"{(i-1)*0.07:.2f}s"
            st.markdown(f"""
            <div class="crc{cls}" style="animation-delay:{delay}">
                <span class="crc-rank">{icon}</span>
                <span class="crc-emoji">{crop_emoji(c)}</span>
                <div class="crc-info">
                    <div class="crc-name">{c.title()}</div>
                    <div class="crc-hint">💧 {m['water']} water · 📦 {m['yield']}</div>
                </div>
                <div class="crc-barcol">
                    <div class="crc-barbg">
                        <div class="crc-fill" style="width:{bar}%;animation-delay:{delay}"></div>
                    </div>
                    <div class="crc-lbl">confidence</div>
                </div>
                <span class="crc-pct">{pct:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with rr:
        st.markdown('<div class="gc"><div class="gc-title">📡 Crop Radar</div>', unsafe_allow_html=True)
        st.plotly_chart(crop_radar(recs), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="gc"><div class="gc-title">📊 Confidence Scores</div>', unsafe_allow_html=True)
        st.plotly_chart(confidence_bars(recs), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Weather data used ─────────────────────────────────────────
    _render_weather_used(weather)


def _render_weather_used(weather: dict[str, Any]) -> None:
    temp = weather.get("temperature_c")
    hum  = weather.get("relative_humidity_pct")
    rain = weather.get("rainfall_mm", 0.0)

    def _f(v: Any, unit: str) -> str:
        return f"{v:.1f}{unit}" if v is not None else "—"

    st.markdown(f"""
    <div class="gc">
        <div class="gc-title">🌤 Live Weather Data Used for This Prediction</div>
        <div class="wg">
            <div class="wc">
                <div class="wc-ico">🌡️</div>
                <div class="wc-lbl">Temperature</div>
                <div class="wc-val">{_f(temp,'')}</div>
                <div class="wc-unit">°C</div>
            </div>
            <div class="wc">
                <div class="wc-ico">💧</div>
                <div class="wc-lbl">Humidity</div>
                <div class="wc-val">{_f(hum,'')}</div>
                <div class="wc-unit">%</div>
            </div>
            <div class="wc">
                <div class="wc-ico">🌧️</div>
                <div class="wc-lbl">Rainfall</div>
                <div class="wc-val">{_f(rain,'')}</div>
                <div class="wc-unit">mm</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    msg, level = irrigation_advice(float(rain) if rain is not None else 0.0)
    st.markdown(f'<div class="alert alert-{level}">{msg}</div>', unsafe_allow_html=True)


def _show_error_help(status: int) -> None:
    if status == 422:
        st.markdown("""
        <div class="alert alert-warn">
          422 Unprocessable Entity — check your input values are within valid ranges
          (N/P/K: 0–300, pH: 0–14, lat: −90 to 90, lon: −180 to 180).
        </div>
        """, unsafe_allow_html=True)
    elif status == 503:
        st.markdown("""
        <div class="alert alert-warn">
          503 Service Unavailable — the weather or inference service could not be reached.
          Check your internet connection and try again.
        </div>
        """, unsafe_allow_html=True)
    elif status >= 500:
        st.markdown("""
        <div class="alert alert-danger">
          Server error. The backend may be temporarily unavailable. Try again shortly.
        </div>
        """, unsafe_allow_html=True)
