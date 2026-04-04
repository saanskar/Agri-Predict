"""
@design-guard
role: Farmer-friendly UI — visually rich, animated, mobile-responsive.
layer: ui
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, cast

import httpx
import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ui.components.geolocation import get_browser_location  # noqa: E402


def _api_base_url() -> str:
    return os.environ.get("AGRIPREDICT_API_BASE_URL", "https://agri-predict-v4em.onrender.com")


def _post_recommendations(payload: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(f"{_api_base_url()}/recommendations", json=payload)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())


# ─────────────────────────────────────────────────────────────────────────────
#  CSS + JS injection
# ─────────────────────────────────────────────────────────────────────────────
def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

        /* ─── Keyframes ─────────────────────────────────────────────────── */
        @keyframes gradientShift {
            0%   { background-position: 0%   50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0%   50%; }
        }
        @keyframes floatUp {
            0%,100% { transform: translateY(0px);   }
            50%      { transform: translateY(-12px); }
        }
        @keyframes fadeSlideIn {
            from { opacity:0; transform:translateY(28px); }
            to   { opacity:1; transform:translateY(0);    }
        }
        @keyframes fadeSlideLeft {
            from { opacity:0; transform:translateX(-24px); }
            to   { opacity:1; transform:translateX(0);     }
        }
        @keyframes pulseGlow {
            0%,100% { box-shadow: 0 0 18px rgba(74,220,74,0.25); }
            50%      { box-shadow: 0 0 38px rgba(74,220,74,0.55); }
        }
        @keyframes shimmer {
            0%   { background-position: -400px 0; }
            100% { background-position:  400px 0; }
        }
        @keyframes spin { to { transform:rotate(360deg); } }
        @keyframes orbit {
            0%   { transform:rotate(0deg)   translateX(70px) rotate(0deg);   }
            100% { transform:rotate(360deg) translateX(70px) rotate(-360deg); }
        }
        @keyframes scaleIn {
            from { opacity:0; transform:scale(.85); }
            to   { opacity:1; transform:scale(1);   }
        }
        @keyframes barFill {
            from { width:0%; }
        }
        @keyframes borderDance {
            0%   { border-color: rgba(74,220,74,.18); }
            50%  { border-color: rgba(120,255,120,.35); }
            100% { border-color: rgba(74,220,74,.18);  }
        }
        @keyframes particleDrift {
            0%   { transform:translateY(0)   translateX(0);   opacity:0; }
            10%  { opacity:.7; }
            90%  { opacity:.4; }
            100% { transform:translateY(-120px) translateX(40px); opacity:0; }
        }

        /* ─── Global ────────────────────────────────────────────────────── */
        *, *::before, *::after { box-sizing:border-box; }
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #d4f5d4; }
        #MainMenu, footer, header { visibility:hidden; }

        /* ─── Animated page background ─────────────────────────────────── */
        .stApp {
            background: linear-gradient(130deg, #050f06 0%, #0a1f0c 20%, #061409 40%, #0d2210 60%, #050f06 80%, #091808 100%);
            background-size: 400% 400%;
            animation: gradientShift 14s ease infinite;
        }

        /* ─── Floating particles ────────────────────────────────────────── */
        .particles { pointer-events:none; position:fixed; inset:0; overflow:hidden; z-index:0; }
        .particle {
            position:absolute; width:6px; height:6px; border-radius:50%;
            background:rgba(74,220,74,.35);
            animation: particleDrift linear infinite;
        }
        .particle:nth-child(1)  { left:8%;  bottom:10%; animation-duration:9s;  animation-delay:0s;   width:4px; height:4px; }
        .particle:nth-child(2)  { left:20%; bottom:20%; animation-duration:13s; animation-delay:2s;   }
        .particle:nth-child(3)  { left:35%; bottom:5%;  animation-duration:11s; animation-delay:4s;   background:rgba(130,255,130,.2); }
        .particle:nth-child(4)  { left:50%; bottom:15%; animation-duration:8s;  animation-delay:1s;   width:3px; height:3px; }
        .particle:nth-child(5)  { left:65%; bottom:8%;  animation-duration:15s; animation-delay:3s;   }
        .particle:nth-child(6)  { left:80%; bottom:25%; animation-duration:10s; animation-delay:6s;   width:4px; height:4px; }
        .particle:nth-child(7)  { left:92%; bottom:12%; animation-duration:12s; animation-delay:.5s;  width:3px; height:3px; }
        .particle:nth-child(8)  { left:15%; bottom:40%; animation-duration:14s; animation-delay:7s;   }
        .particle:nth-child(9)  { left:75%; bottom:50%; animation-duration:9s;  animation-delay:2.5s; width:5px; height:5px; }
        .particle:nth-child(10) { left:45%; bottom:60%; animation-duration:16s; animation-delay:5s;   width:3px; height:3px; }

        /* ─── Hero ──────────────────────────────────────────────────────── */
        .hero-wrap {
            position:relative; border-radius:24px;
            padding:3rem 2.5rem 2.5rem; margin-bottom:2rem;
            overflow:hidden;
            background:linear-gradient(135deg,rgba(10,30,12,.95) 0%,rgba(18,52,22,.95) 50%,rgba(10,30,12,.95) 100%);
            border:1px solid rgba(74,220,74,.22);
            animation: pulseGlow 4s ease-in-out infinite, fadeSlideIn .8s ease both;
        }
        .hero-wrap::before {
            content:''; position:absolute; inset:0;
            background:linear-gradient(90deg,transparent 0%,rgba(74,220,74,.06) 50%,transparent 100%);
            background-size:200% 100%;
            animation: shimmer 3s linear infinite;
        }
        .hero-grid {
            position:absolute; inset:0;
            background-image:linear-gradient(rgba(74,220,74,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(74,220,74,.04) 1px,transparent 1px);
            background-size:40px 40px;
        }
        .hero-orb {
            position:absolute; right:2.5rem; top:50%;
            transform:translateY(-50%);
            width:110px; height:110px;
        }
        .orb-core {
            width:70px; height:70px; border-radius:50%;
            background:radial-gradient(circle,rgba(74,220,74,.35) 0%,rgba(20,80,20,.15) 70%,transparent 100%);
            position:absolute; top:50%; left:50%;
            transform:translate(-50%,-50%);
            animation:floatUp 4s ease-in-out infinite;
            display:flex; align-items:center; justify-content:center;
            font-size:2rem;
        }
        .orb-ring  { position:absolute; inset:0;   border-radius:50%; border:1.5px dashed rgba(74,220,74,.3); animation:spin 12s linear infinite; }
        .orb-ring2 { position:absolute; inset:8px; border-radius:50%; border:1px solid rgba(74,220,74,.15);   animation:spin 8s linear infinite reverse; }
        .orb-dot   {
            width:10px; height:10px; border-radius:50%;
            background:#4adc4a; box-shadow:0 0 12px rgba(74,220,74,.7);
            animation:orbit 4s linear infinite;
            position:absolute; top:50%; left:50%; margin-top:-5px; margin-left:-5px;
        }
        .hero-badge {
            display:inline-block;
            background:rgba(74,220,74,.12); border:1px solid rgba(74,220,74,.3);
            border-radius:99px; padding:.25rem .8rem;
            font-size:.7rem; letter-spacing:2px; text-transform:uppercase;
            color:#4adc4a; margin-bottom:.8rem;
            animation:fadeSlideLeft .6s ease both;
        }
        .hero-title {
            font-weight:900; font-size:clamp(2rem,5vw,3.5rem);
            line-height:1.05; letter-spacing:-1px; color:#fff;
            text-shadow:0 0 40px rgba(74,220,74,.25);
            animation:fadeSlideIn .9s ease both; margin-bottom:.6rem;
        }
        .hero-title span {
            background:linear-gradient(135deg,#4adc4a,#a8f5a8,#4adc4a);
            background-size:200% 100%;
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            animation:gradientShift 3s ease infinite;
        }
        .hero-sub { color:rgba(180,230,180,.7); font-size:.95rem; font-weight:300; animation:fadeSlideIn 1s ease both .2s; }
        .hero-pills { display:flex; gap:.5rem; flex-wrap:wrap; margin-top:1.2rem; animation:fadeSlideIn 1s ease both .35s; }
        .hero-pill { background:rgba(74,220,74,.1); border:1px solid rgba(74,220,74,.2); border-radius:99px; padding:.18rem .7rem; font-size:.72rem; color:#90e890; }

        /* ─── Section cards ─────────────────────────────────────────────── */
        .scard {
            background:rgba(12,28,14,.8); border:1px solid rgba(74,220,74,.18);
            border-radius:20px; padding:1.8rem 1.6rem 1.4rem;
            margin-bottom:1.5rem; backdrop-filter:blur(12px);
            animation:fadeSlideIn .6s ease both, borderDance 5s ease-in-out infinite;
            position:relative; overflow:hidden;
        }
        .scard::after {
            content:''; position:absolute; top:-1px; left:20%; right:20%; height:2px;
            background:linear-gradient(90deg,transparent,rgba(74,220,74,.5),transparent);
            border-radius:99px;
        }
        .scard-title {
            font-weight:700; font-size:.7rem; letter-spacing:3px;
            text-transform:uppercase; color:#4adc4a; margin-bottom:1.2rem;
            display:flex; align-items:center; gap:.5rem;
        }
        .scard-title::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(74,220,74,.3),transparent); }

        /* ─── Inputs ────────────────────────────────────────────────────── */
        .stNumberInput label, .stSelectbox label, .stSlider label, .stTextInput label {
            color:#90e890 !important; font-size:.83rem !important; font-weight:500 !important;
        }
        .stNumberInput input, .stTextInput input {
            background:rgba(6,18,8,.9) !important; border:1px solid rgba(74,220,74,.25) !important;
            border-radius:12px !important; color:#e0f5e0 !important;
            font-family:'Outfit',sans-serif !important; font-size:.9rem !important;
            transition:border-color .25s,box-shadow .25s !important;
        }
        .stNumberInput input:focus, .stTextInput input:focus {
            border-color:#4adc4a !important; box-shadow:0 0 0 3px rgba(74,220,74,.18) !important;
        }
        div[data-baseweb="select"] > div {
            background:rgba(6,18,8,.9) !important; border:1px solid rgba(74,220,74,.25) !important;
            border-radius:12px !important; color:#e0f5e0 !important; transition:border-color .25s !important;
        }
        div[data-baseweb="select"] > div:hover { border-color:rgba(74,220,74,.5) !important; }
        li[role="option"] { background:rgba(10,25,12,.98) !important; color:#d4f5d4 !important; }
        li[role="option"]:hover { background:rgba(74,220,74,.15) !important; }

        /* ─── Metric boxes ──────────────────────────────────────────────── */
        .metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; margin-top:1rem; }
        @media(max-width:640px){ .metric-grid{ grid-template-columns:repeat(2,1fr); } }
        .mbox {
            background:linear-gradient(145deg,rgba(16,42,18,.9),rgba(8,22,10,.9));
            border:1px solid rgba(74,220,74,.2); border-radius:14px;
            padding:1rem .8rem; text-align:center;
            transition:transform .2s,border-color .2s,box-shadow .2s;
            animation:scaleIn .5s ease both;
        }
        .mbox:hover { transform:translateY(-4px) scale(1.03); border-color:rgba(74,220,74,.5); box-shadow:0 8px 28px rgba(74,220,74,.15); }
        .mbox-label { font-size:.65rem; letter-spacing:2.5px; text-transform:uppercase; color:#4adc4a; margin-bottom:.35rem; }
        .mbox-value { font-family:'Space Mono',monospace; font-size:1.4rem; font-weight:700; color:#a8f5a8; }
        .mbox-unit  { font-size:.62rem; color:rgba(74,220,74,.6); margin-left:.15rem; }

        /* ─── Buttons ───────────────────────────────────────────────────── */
        .stButton button[kind="primary"] {
            position:relative; overflow:hidden;
            background:linear-gradient(135deg,#1d6b1d,#4adc4a,#1d6b1d) !important;
            background-size:200% 100% !important; border:none !important;
            border-radius:14px !important; color:#fff !important;
            font-family:'Outfit',sans-serif !important; font-weight:700 !important; font-size:1rem !important;
            padding:.75rem 2rem !important; width:100%;
            box-shadow:0 4px 24px rgba(74,220,74,.35) !important;
            transition:background-position .4s,transform .2s,box-shadow .2s !important;
            animation:pulseGlow 3s ease-in-out infinite !important;
        }
        .stButton button[kind="primary"]::before {
            content:''; position:absolute; inset:0;
            background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,.15) 50%,transparent 100%);
            background-size:200% 100%; animation:shimmer 2s linear infinite;
        }
        .stButton button[kind="primary"]:hover {
            background-position:100% 0 !important; transform:translateY(-3px) !important;
            box-shadow:0 10px 36px rgba(74,220,74,.5) !important;
        }
        .stButton button[kind="secondary"] {
            background:rgba(74,220,74,.07) !important; border:1px solid rgba(74,220,74,.3) !important;
            border-radius:12px !important; color:#90e890 !important;
            font-family:'Outfit',sans-serif !important; font-weight:500 !important;
            width:100%; transition:all .25s !important;
        }
        .stButton button[kind="secondary"]:hover {
            background:rgba(74,220,74,.15) !important; border-color:#4adc4a !important;
            transform:translateY(-2px) !important; box-shadow:0 4px 18px rgba(74,220,74,.2) !important;
        }

        /* ─── Weather metrics ───────────────────────────────────────────── */
        [data-testid="metric-container"] {
            background:rgba(12,28,14,.85) !important; border:1px solid rgba(74,220,74,.2) !important;
            border-radius:14px !important; padding:.8rem 1rem !important;
            animation:scaleIn .5s ease both; transition:border-color .2s,box-shadow .2s !important;
        }
        [data-testid="metric-container"]:hover { border-color:rgba(74,220,74,.45) !important; box-shadow:0 6px 22px rgba(74,220,74,.12) !important; }
        [data-testid="stMetricLabel"] { color:#90e890 !important; font-size:.78rem !important; }
        [data-testid="stMetricValue"] { color:#a8f5a8 !important; font-family:'Space Mono',monospace !important; font-size:1.3rem !important; }

        /* ─── Crop cards ────────────────────────────────────────────────── */
        .crop-card {
            display:flex; align-items:center; gap:.8rem;
            background:rgba(10,25,12,.85); border:1px solid rgba(74,220,74,.15);
            border-radius:16px; padding:1rem 1.2rem; margin-bottom:.7rem;
            transition:transform .25s,border-color .25s,box-shadow .25s;
            animation:fadeSlideLeft .5s ease both;
        }
        .crop-card:hover { transform:translateX(6px) scale(1.01); border-color:rgba(74,220,74,.45); box-shadow:0 6px 28px rgba(74,220,74,.12); }
        .crop-card.top1  { background:linear-gradient(135deg,rgba(16,50,18,.95),rgba(10,30,12,.95)); border-color:rgba(74,220,74,.4); box-shadow:0 0 28px rgba(74,220,74,.12); }
        .crop-rank  { font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:rgba(74,220,74,.4); min-width:2rem; text-align:center; }
        .crop-emoji { font-size:1.4rem; min-width:2rem; text-align:center; }
        .crop-name  { font-weight:700; font-size:1.02rem; color:#d4f5d4; flex:1; text-transform:capitalize; }
        .crop-bar-col { flex:2; }
        .crop-bar-bg   { background:rgba(74,220,74,.1); border-radius:99px; height:8px; overflow:hidden; margin-bottom:.25rem; }
        .crop-bar-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#1d6b1d,#4adc4a,#a8f5a8); animation:barFill .9s cubic-bezier(.4,0,.2,1) both; }
        .crop-bar-lbl  { font-size:.66rem; color:rgba(74,220,74,.55); font-family:'Space Mono',monospace; }
        .crop-pct { font-family:'Space Mono',monospace; font-weight:700; font-size:.95rem; color:#a8f5a8; min-width:4rem; text-align:right; }

        /* ─── Misc ──────────────────────────────────────────────────────── */
        .stAlert  { border-radius:14px !important; }
        .stSpinner > div { border-top-color:#4adc4a !important; }
        hr { border-color:rgba(74,220,74,.12) !important; }
        .streamlit-expanderHeader { background:rgba(12,28,14,.8) !important; border-radius:12px !important; color:#90e890 !important; }
        pre { border-radius:12px !important; font-size:.8rem !important; }

        @media(max-width:640px){
            .hero-orb { display:none; }
            .hero-title { font-size:2rem; }
            .scard { padding:1.3rem 1.1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_particles() -> None:
    st.markdown(
        '<div class="particles">' + ("".join('<div class="particle"></div>' for _ in range(10))) + "</div>",
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-grid"></div>
            <div class="hero-badge">🌱 AI-Powered Agriculture</div>
            <div class="hero-title">Agri<span>Predict</span></div>
            <div class="hero-sub">Precision crop recommendations · Soil NPK + pH · Live weather intelligence</div>
            <div class="hero-pills">
                <span class="hero-pill">🧪 Soil Analysis</span>
                <span class="hero-pill">🌦 Live Weather</span>
                <span class="hero-pill">🤖 ML Predictions</span>
                <span class="hero-pill">📍 GPS Location</span>
            </div>
            <div class="hero-orb">
                <div class="orb-ring"></div>
                <div class="orb-ring2"></div>
                <div class="orb-core">🌾</div>
                <div class="orb-dot"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_CROP_EMOJI: dict[str, str] = {
    "rice":"🌾","wheat":"🌾","maize":"🌽","corn":"🌽","cotton":"🌿",
    "sugarcane":"🎋","jute":"🌱","coffee":"☕","banana":"🍌","mango":"🥭",
    "grapes":"🍇","watermelon":"🍉","apple":"🍎","orange":"🍊","papaya":"🍈",
    "pomegranate":"🍎","coconut":"🥥","chickpea":"🫘","lentil":"🫘",
    "mungbean":"🫘","blackgram":"🫘","kidney beans":"🫘","moth beans":"🫘",
    "pigeonpeas":"🫘","soybean":"🫛",
}


def _crop_emoji(name: str) -> str:
    return _CROP_EMOJI.get(name.lower().strip(), "🌿")


def _render_crop_results(recs: list[dict[str, Any]]) -> None:
    st.markdown('<div class="scard"><div class="scard-title">🏆 Top Crop Recommendations</div>', unsafe_allow_html=True)
    max_prob = max((float(r.get("probability", 0)) for r in recs), default=1) or 1
    for i, r in enumerate(recs, 1):
        crop  = str(r.get("crop", "Unknown"))
        prob  = float(r.get("probability", 0.0))
        pct   = prob * 100
        bar   = max(2, round(prob / max_prob * 100))
        emoji = _crop_emoji(crop)
        top_class = " top1" if i == 1 else ""
        delay = f"{(i-1)*0.1:.1f}s"
        st.markdown(
            f"""
            <div class="crop-card{top_class}" style="animation-delay:{delay}">
                <span class="crop-rank">{'🥇' if i==1 else f'#{i}'}</span>
                <span class="crop-emoji">{emoji}</span>
                <span class="crop-name">{crop.title()}</span>
                <div class="crop-bar-col">
                    <div class="crop-bar-bg">
                        <div class="crop-bar-fill" style="width:{bar}%;animation-delay:{delay}"></div>
                    </div>
                    <div class="crop-bar-lbl">confidence</div>
                </div>
                <span class="crop-pct">{pct:.1f}%</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="AgriPredict", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
    _inject_styles()
    _render_particles()
    _render_hero()

    for key, val in [("lat", 20.0), ("lon", 78.0), ("request_geo", False)]:
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Soil Parameters ──────────────────────────────────────────
    st.markdown('<div class="scard"><div class="scard-title">🧪 Soil Parameters</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        n  = st.number_input("Nitrogen (N) — kg/ha",   min_value=0.0, max_value=300.0, value=50.0, step=1.0)
        k  = st.number_input("Potassium (K) — kg/ha",  min_value=0.0, max_value=300.0, value=40.0, step=1.0)
    with c2:
        p  = st.number_input("Phosphorus (P) — kg/ha", min_value=0.0, max_value=300.0, value=40.0, step=1.0)
        ph = st.number_input("Soil pH",                min_value=0.0, max_value=14.0,  value=6.5,  step=0.1)
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="mbox" style="animation-delay:.0s"><div class="mbox-label">Nitrogen N</div><div class="mbox-value">{n:.0f}<span class="mbox-unit">kg/ha</span></div></div>
            <div class="mbox" style="animation-delay:.1s"><div class="mbox-label">Phosphorus P</div><div class="mbox-value">{p:.0f}<span class="mbox-unit">kg/ha</span></div></div>
            <div class="mbox" style="animation-delay:.2s"><div class="mbox-label">Potassium K</div><div class="mbox-value">{k:.0f}<span class="mbox-unit">kg/ha</span></div></div>
            <div class="mbox" style="animation-delay:.3s"><div class="mbox-label">Soil pH</div><div class="mbox-value">{ph:.1f}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="scard"><div class="scard-title">🌦 Agronomic Context</div>', unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        season    = st.selectbox("Growing Season", ["Kharif (Jun–Nov)", "Rabi (Nov–Apr)", "Zaid (Apr–Jun)", "Year-round"])
        soil_type = st.selectbox("Soil Type",      ["Alluvial", "Black / Regur", "Red & Laterite", "Arid / Desert", "Forest / Mountain", "Other"])
    with a2:
        irrigation = st.selectbox("Irrigation",    ["Rain-fed only", "Canal irrigation", "Drip / Sprinkler", "Borewell / Tube well"])
        farm_size  = st.number_input("Farm Area (acres)", min_value=0.1, max_value=5000.0, value=2.0, step=0.5)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Location ─────────────────────────────────────────────────
    st.markdown('<div class="scard"><div class="scard-title">📍 Location</div>', unsafe_allow_html=True)
    if st.button("📡 Use My Current Location (Browser)", key="geo_btn"):
        st.session_state["request_geo"] = True
    if st.session_state.get("request_geo", False):
        loc = get_browser_location(timeout_ms=10_000, key="browser_geo")
        if isinstance(loc, dict) and "lat" in loc and "lon" in loc:
            st.session_state["lat"] = float(loc["lat"])
            st.session_state["lon"] = float(loc["lon"])
            st.session_state["request_geo"] = False
            st.success("✅ Location updated from browser.")
        elif isinstance(loc, dict) and "error" in loc:
            st.session_state["request_geo"] = False
            st.error(f"Could not get location: {loc.get('error')}")
        elif isinstance(loc, dict) and "status" in loc:
            st.info(f"Location status: {loc.get('status')} {loc.get('state','')}".strip())
        else:
            st.info("Waiting for browser location… (Use the Local URL if on the Network URL)")
    lc1, lc2 = st.columns(2)
    with lc1:
        lat = st.number_input("Latitude",  min_value=-90.0,  max_value=90.0,  step=0.01, key="lat")
    with lc2:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, step=0.01, key="lon")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Settings ──────────────────────────────────────────────────
    st.markdown('<div class="scard"><div class="scard-title">⚙️ Recommendation Settings</div>', unsafe_allow_html=True)
    top_k = st.slider("How many crops to recommend?", min_value=1, max_value=10, value=5)
    st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.button("🌱 Get Crop Recommendations", type="primary", key="submit_btn")

    if submitted:
        payload: dict[str, Any] = {
            "location": {"lat": float(lat), "lon": float(lon)},
            "soil":     {"n": float(n), "p": float(p), "k": float(k), "ph": float(ph)},
            "top_k":    int(top_k),
            "context":  {"season": season, "soil_type": soil_type, "irrigation": irrigation, "farm_size": float(farm_size)},
        }
        with st.spinner("🔄  Analysing soil · Fetching live weather · Running ML model…"):
            try:
                data = _post_recommendations(payload)
            except httpx.HTTPStatusError as exc:
                st.error(f"⚠️ API error {exc.response.status_code}: {exc.response.text}")
                return
            except Exception as exc:
                st.error(f"⚠️ Request failed: {exc}")
                return

        st.success("✅ Analysis complete — here are your recommendations!")

        weather = data.get("weather", {})

        if weather:
            st.markdown(
                '<div class="scard"><div class="scard-title">🌤 Live Weather Data Used</div>',
                unsafe_allow_html=True
            )

            # ✅ Support both backend formats
            temperature = weather.get("temperature_c") or weather.get("temperature_2m")
            humidity = weather.get("relative_humidity_pct") or weather.get("relative_humidity_2m")
            rainfall = weather.get("rainfall_mm") or weather.get("precipitation")

            w1, w2, w3 = st.columns(3)

            w1.metric("🌡 Temperature", f"{temperature if temperature is not None else '—'} °C")
            w2.metric("💧 Humidity", f"{humidity if humidity is not None else '—'} %")
            w3.metric("🌧 Rainfall", f"{rainfall if rainfall is not None else '—'} mm")

            # ✅ Rainfall intelligence (NEW FEATURE 🔥)
            if rainfall is not None:
                if rainfall == 0:
                    st.info("☀️ No rainfall — irrigation required.")
                elif rainfall < 10:
                    st.info("🌦 Light rainfall — moderate water availability.")
                else:
                    st.warning("🌧 Heavy rainfall — avoid over-irrigation.")

            st.markdown("</div>", unsafe_allow_html=True)

        recs = data.get("recommendations", [])
        if not recs:
            st.warning("⚠️ No recommendations returned.")
        else:
            _render_crop_results(recs)


if __name__ == "__main__":
    main()