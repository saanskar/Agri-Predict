"""
AgriPredict — Predict Crop Page
=================================
User selects State + Season → weather auto-fills.
User enters Soil (N, P, K, pH) from their soil test report.
All 7 values go directly to the model — no API guessing.
"""
from __future__ import annotations
from typing import Any
import streamlit as st
from charts import confidence_bars, crop_radar, npk_bar
from utils  import (
    APIError, NetworkError,
    call_recommendations, crop_emoji, crop_meta,
    irrigation_advice, push_history,
)

try:
    from components.geolocation import get_browser_location
    _GEO_OK = True
except Exception:
    _GEO_OK = False

# ── State + Season → Climate lookup (IMD normals) ─────────────────────────────
# Format: (avg_temp_C, avg_humidity_%, avg_monthly_rainfall_mm)
CLIMATE: dict[str, dict[str, tuple[float,float,float]]] = {
    "Bihar":            {"Kharif":(28,78,150), "Rabi":(18,60,20),  "Zaid":(35,45,15)},
    "Gujarat":          {"Kharif":(30,72,80),  "Rabi":(22,50,10),  "Zaid":(38,35,5)},
    "Jharkhand":        {"Kharif":(27,80,180), "Rabi":(17,58,25),  "Zaid":(34,42,12)},
    "Karnataka":        {"Kharif":(24,75,130), "Rabi":(20,60,40),  "Zaid":(30,45,20)},
    "Madhya Pradesh":   {"Kharif":(28,73,140), "Rabi":(18,52,18),  "Zaid":(38,30,8)},
    "Maharashtra":      {"Kharif":(27,75,120), "Rabi":(22,55,15),  "Zaid":(36,35,10)},
    "Punjab":           {"Kharif":(30,70,130), "Rabi":(14,58,25),  "Zaid":(38,32,8)},
    "Tamil Nadu":       {"Kharif":(28,78,90),  "Rabi":(25,72,150), "Zaid":(33,55,30)},
    "Uttar Pradesh":    {"Kharif":(29,74,150), "Rabi":(16,58,22),  "Zaid":(37,35,10)},
    "West Bengal":      {"Kharif":(29,85,230), "Rabi":(20,68,25),  "Zaid":(34,55,15)},
    "Other / Manual":   {"Kharif":(28,75,120), "Rabi":(20,58,30),  "Zaid":(35,38,15)},
}

SEASON_INFO = {
    "Kharif": "☔ Kharif — Monsoon season (June to October). Main crops: Rice, Maize, Cotton, Jute.",
    "Rabi":   "❄️ Rabi — Winter season (November to March). Main crops: Chickpea, Lentil, Wheat.",
    "Zaid":   "☀️ Zaid — Summer season (March to May). Main crops: Watermelon, Muskmelon, Mungbean.",
}

SOIL_EXAMPLES = {
    "Rice":        (80,  49,  39,  6.4),
    "Maize":       (78,  48,  20,  6.3),
    "Cotton":      (117, 45,  19,  6.9),
    "Jute":        (78,  47,  40,  6.7),
    "Coffee":      (103, 29,  30,  6.8),
    "Banana":      (99,  81,  50,  6.0),
    "Chickpea":    (39,  68,  80,  7.4),
    "Lentil":      (18,  69,  19,  6.9),
    "Muskmelon":   (101, 19,  51,  6.4),
    "Watermelon":  (100, 17,  50,  6.5),
    "Apple":       (23,  135, 199, 5.9),
    "Grapes":      (22,  132, 200, 6.0),
    "Mango":       (20,  29,  29,  5.7),
    "Coconut":     (23,  16,  31,  5.9),
    "Papaya":      (49,  59,  50,  6.7),
    "Orange":      (20,  17,  10,  7.1),
    "Pomegranate": (17,  19,  40,  6.5),
    "Pigeonpeas":  (21,  69,  20,  5.7),
    "Mothbeans":   (22,  48,  21,  7.0),
    "Mungbean":    (21,  48,  20,  6.7),
    "Blackgram":   (41,  67,  19,  7.2),
    "Kidneybeans": (20,  68,  20,  5.8),
    "Custom":      (None, None, None, None),
}


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>🌱 Predict Optimal Crop</h1>
        <p>Select your state and season — weather fills automatically. Enter your soil test values.</p>
    </div>
    """, unsafe_allow_html=True)

    form_col, prev_col = st.columns([1.2, 1], gap="medium")

    with form_col:

        # ── STEP 1: STATE + SEASON ────────────────────────────────
        st.markdown('<div class="gc"><div class="gc-title">📍 Step 1 — Your Location & Season</div>',
                    unsafe_allow_html=True)

        s1, s2 = st.columns(2)
        with s1:
            state = st.selectbox("Select Your State",
                                  list(CLIMATE.keys()),
                                  index=0,
                                  help="Choose the state where you want to grow the crop")
        with s2:
            season = st.selectbox("Select Season",
                                   ["Kharif", "Rabi", "Zaid"],
                                   help="Kharif=Monsoon, Rabi=Winter, Zaid=Summer")

        # Show season info
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                    padding:0.6rem 0.9rem;font-size:0.82rem;color:#15803D;margin-top:0.4rem">
            {SEASON_INFO[season]}
        </div>
        """, unsafe_allow_html=True)

        # Auto-fill weather from state+season
        auto_temp, auto_hum, auto_rain = CLIMATE[state][season]
        st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 2: SOIL ──────────────────────────────────────────
        st.markdown('<div class="gc"><div class="gc-title">🧪 Step 2 — Soil Parameters (from soil test)</div>',
                    unsafe_allow_html=True)

        # Quick-fill from crop examples
        fill_crop = st.selectbox(
            "Quick-fill soil values for a specific crop (optional)",
            list(SOIL_EXAMPLES.keys()),
            index=list(SOIL_EXAMPLES.keys()).index("Custom"),
            help="Select a crop to auto-fill typical soil values, or choose Custom to enter manually"
        )
        ex_n, ex_p, ex_k, ex_ph = SOIL_EXAMPLES[fill_crop]

        c1, c2 = st.columns(2)
        with c1:
            n  = st.number_input("Nitrogen (N) kg/ha",
                                  min_value=0.0, max_value=200.0,
                                  value=float(ex_n if ex_n else st.session_state.get("n", 80.0)),
                                  step=1.0)
            k  = st.number_input("Potassium (K) kg/ha",
                                  min_value=0.0, max_value=250.0,
                                  value=float(ex_k if ex_k else st.session_state.get("k", 40.0)),
                                  step=1.0)
        with c2:
            p  = st.number_input("Phosphorus (P) kg/ha",
                                  min_value=0.0, max_value=200.0,
                                  value=float(ex_p if ex_p else st.session_state.get("p", 48.0)),
                                  step=1.0)
            ph = st.number_input("Soil pH",
                                  min_value=0.0, max_value=14.0,
                                  value=float(ex_ph if ex_ph else st.session_state.get("ph", 6.5)),
                                  step=0.1)

        st.markdown(f"""
        <div class="ir" style="margin-top:0.6rem">
            <div class="ib"><div class="ib-l">N</div><div class="ib-v">{n:.0f}</div></div>
            <div class="ib"><div class="ib-l">P</div><div class="ib-v">{p:.0f}</div></div>
            <div class="ib"><div class="ib-l">K</div><div class="ib-v">{k:.0f}</div></div>
            <div class="ib"><div class="ib-l">pH</div><div class="ib-v">{ph:.1f}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 3: WEATHER (auto-filled, user can override) ──────
        st.markdown('<div class="gc"><div class="gc-title">🌤 Step 3 — Weather (auto-filled from State + Season)</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#EFF6FF;border:1px solid #93C5FD;border-radius:8px;
                    padding:0.5rem 0.75rem;font-size:0.78rem;color:#1D4ED8;margin-bottom:0.7rem">
            ℹ️ Auto-filled for <strong>{state} — {season}</strong>.
            You can adjust if you know your exact local values.
        </div>
        """, unsafe_allow_html=True)

        w1, w2, w3 = st.columns(3)
        with w1:
            temperature = st.number_input("Temperature (°C)",
                                           min_value=0.0, max_value=50.0,
                                           value=float(auto_temp), step=0.5)
        with w2:
            humidity    = st.number_input("Humidity (%)",
                                           min_value=0.0, max_value=100.0,
                                           value=float(auto_hum), step=1.0)
        with w3:
            rainfall    = st.number_input("Rainfall (mm/month)",
                                           min_value=0.0, max_value=400.0,
                                           value=float(auto_rain), step=5.0)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── LOCATION (display only) ───────────────────────────────
        with st.expander("📍 GPS Location (optional — for map display only)"):
            if _GEO_OK:
                if st.button("📡 Use My GPS", key="geo_btn"):
                    st.session_state.request_geo = True
                if st.session_state.get("request_geo"):
                    loc = get_browser_location(timeout_ms=12_000, key="geo_predict")
                    if isinstance(loc, dict):
                        if "lat" in loc:
                            st.session_state.lat = float(loc["lat"])
                            st.session_state.lon = float(loc["lon"])
                            st.session_state.request_geo = False
                            st.success(f"✅ {loc['lat']:.4f}°, {loc['lon']:.4f}°")
                        elif "error" in loc:
                            st.session_state.request_geo = False
                        else:
                            st.info("Waiting for GPS…")
            lc, rc = st.columns(2)
            with lc:
                lat = st.number_input("Latitude",  -90.0, 90.0,
                                       float(st.session_state.get("lat") or 20.0),
                                       step=0.0001, format="%.4f")
            with rc:
                lon = st.number_input("Longitude",-180.0,180.0,
                                       float(st.session_state.get("lon") or 78.0),
                                       step=0.0001, format="%.4f")

        top_k = st.slider("Crops to recommend", 1, 10,
                           int(st.session_state.get("top_k", 5)))

        submitted = st.button("🌾 Get Crop Recommendations",
                               type="primary", key="submit")

    # ── PREVIEW COLUMN ────────────────────────────────────────────
    with prev_col:
        st.markdown('<div class="gc"><div class="gc-title">📊 NPK Preview</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(npk_bar(n, p, k), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="gc">
            <div class="gc-title">🌤 Weather for {state} — {season}</div>
            <div class="wg">
                <div class="wc">
                    <div class="wc-ico">🌡️</div>
                    <div class="wc-lbl">Temp</div>
                    <div class="wc-val" style="font-size:1.2rem">{temperature:.0f}</div>
                    <div class="wc-unit">°C</div>
                </div>
                <div class="wc">
                    <div class="wc-ico">💧</div>
                    <div class="wc-lbl">Humidity</div>
                    <div class="wc-val" style="font-size:1.2rem">{humidity:.0f}</div>
                    <div class="wc-unit">%</div>
                </div>
                <div class="wc">
                    <div class="wc-ico">🌧️</div>
                    <div class="wc-lbl">Rainfall</div>
                    <div class="wc-val" style="font-size:1.2rem">{rainfall:.0f}</div>
                    <div class="wc-unit">mm</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="gc">
            <div class="gc-title">📖 Soil Test Ranges</div>
            <div style="font-size:0.8rem;color:#374151;line-height:2">
                <strong style="color:#16A34A">N</strong> 0–149 kg/ha<br>
                <strong style="color:#16A34A">P</strong> 0–158 kg/ha<br>
                <strong style="color:#16A34A">K</strong> 0–222 kg/ha<br>
                <strong style="color:#16A34A">pH</strong> 3.5–10.0<br>
                <span style="font-size:0.72rem;color:#9CA3AF">
                Get these from your soil test lab report
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── API CALL ──────────────────────────────────────────────────
    if submitted:
        st.session_state.update(
            n=n, p=p, k=k, ph=ph,
            lat=lat, lon=lon, top_k=top_k,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
        )
        with st.spinner("🔄 Running ML ensemble…"):
            try:
                data = call_recommendations(
                    lat=lat, lon=lon,
                    n=n, p=p, k=k, ph=ph,
                    temperature_c=temperature,
                    humidity_pct=humidity,
                    rainfall_mm=rainfall,
                    top_k=top_k,
                )
                st.session_state.api_error    = None
                st.session_state.last_result  = data
                st.session_state.last_weather = {
                    "temperature_c":         temperature,
                    "relative_humidity_pct": humidity,
                    "rainfall_mm":           rainfall,
                }
                push_history(st, n, p, k, ph, lat, lon,
                             data.get("recommendations", []),
                             st.session_state.last_weather)
                st.success("✅ Prediction complete!")

            except APIError as exc:
                st.error(f"⚠️ Backend error {exc.status}: {exc.detail}")
                return
            except NetworkError as exc:
                st.error(f"⚠️ {exc}")
                st.markdown("""
                <div class="alert alert-warn">
                Backend cold start — wait 30s and try again.
                </div>""", unsafe_allow_html=True)
                return

    # ── RESULTS ───────────────────────────────────────────────────
    result = st.session_state.last_result
    if not result:
        return

    recs = result.get("recommendations", [])
    if not recs:
        st.warning("No recommendations returned.")
        return

    st.markdown("---")
    if not submitted:
        st.markdown("""<div style="color:#9CA3AF;font-size:0.78rem;margin-bottom:0.5rem">
        📋 Last prediction — submit to refresh</div>""", unsafe_allow_html=True)

    _render_results(recs)


def _render_results(recs: list[dict[str, Any]]) -> None:
    top  = recs[0]
    meta = crop_meta(top["crop"])
    conf = float(top["probability"]) * 100

    suitability = (
        "Excellent Match ✨" if conf > 70 else
        "Good Match 👍"     if conf > 45 else
        "Possible Match ⚠️"
    )

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

    rl, rr = st.columns([1.1, 1], gap="medium")

    with rl:
        st.markdown('<div class="gc"><div class="gc-title">🏆 Recommendations</div>',
                    unsafe_allow_html=True)
        max_p = max(float(r["probability"]) for r in recs) or 1.0
        for i, rec in enumerate(recs, 1):
            c    = rec["crop"]
            prob = float(rec["probability"])
            pct  = prob * 100
            bar  = max(3, round(prob / max_p * 100))
            m    = crop_meta(c)
            icon = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"#{i}"
            cls  = " r1" if i==1 else ""
            st.markdown(f"""
            <div class="crc{cls}">
                <span class="crc-rank">{icon}</span>
                <span class="crc-emoji">{crop_emoji(c)}</span>
                <div class="crc-info">
                    <div class="crc-name">{c.title()}</div>
                    <div class="crc-hint">💧{m['water']} water · 📦{m['yield']}</div>
                </div>
                <div class="crc-barcol">
                    <div class="crc-barbg">
                        <div class="crc-fill" style="width:{bar}%"></div>
                    </div>
                    <div class="crc-lbl">confidence</div>
                </div>
                <span class="crc-pct">{pct:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with rr:
        st.markdown('<div class="gc"><div class="gc-title">📡 Crop Radar</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(crop_radar(recs), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="gc"><div class="gc-title">📊 Confidence</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(confidence_bars(recs), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)