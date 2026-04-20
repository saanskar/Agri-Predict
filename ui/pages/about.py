"""
AgriPredict — About Page
==========================
Project overview, ML architecture, tech stack.
No raw HTML code blocks, no API reference in UI.
"""

from __future__ import annotations
import streamlit as st


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>📖 About AgriPredict</h1>
        <p>AI-driven crop recommendation system combining soil analysis with real-time weather</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Project overview ──────────────────────────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">🌾 What is AgriPredict?</div>
        <p style="color:#374151;font-size:0.9rem;line-height:1.85;margin:0 0 1rem">
            <strong>AgriPredict</strong> is a machine-learning powered crop recommendation system
            that combines <strong style="color:#16A34A">real-time weather data</strong> with
            <strong style="color:#16A34A">soil nutrient analysis</strong> to recommend the crop
            most suited to your field and location.
        </p>
        <p style="color:#374151;font-size:0.9rem;line-height:1.85;margin:0">
            The system uses an ensemble of three models — Random Forest, XGBoost, and a Neural
            Network — whose predictions are averaged for higher accuracy than any single model
            alone. Live weather is fetched automatically from Open-Meteo for the coordinates
            you provide.
        </p>
        <div style="margin-top:1rem;display:flex;gap:0.4rem;flex-wrap:wrap">
            <span class="tag">🤖 ML Ensemble</span>
            <span class="tag">🌦 Live Weather</span>
            <span class="tag">🧪 Soil Analysis</span>
            <span class="tag">📍 GPS Support</span>
            <span class="tag">📊 Interactive Charts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Problem & Solution ────────────────────────────────────────
    lc, rc = st.columns(2, gap="medium")
    with lc:
        st.markdown("""
        <div class="gc" style="height:100%">
            <div class="gc-title">⚠️ The Problem</div>
            <div style="font-size:0.87rem;color:#374151;line-height:2">
                🌾 Many farmers rely on intuition alone<br>
                📉 Wrong crop choice leads to yield loss<br>
                🌡️ Ignoring weather wastes water &amp; inputs<br>
                🧪 Soil test results often go unused<br>
                💸 Expert advisory is costly or unavailable
            </div>
        </div>
        """, unsafe_allow_html=True)
    with rc:
        st.markdown("""
        <div class="gc" style="height:100%">
            <div class="gc-title">✅ Our Solution</div>
            <div style="font-size:0.87rem;color:#374151;line-height:2">
                🤖 Ensemble model: RF + XGBoost + Neural Net<br>
                🌦️ Live weather via Open-Meteo API<br>
                🧪 NPK + pH as direct model features<br>
                📍 GPS-enabled — works from any location<br>
                📱 Mobile-friendly, browser-based
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── ML Architecture — clean visual cards ──────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">🧠 Machine Learning Architecture</div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4, gap="small")
    _card_style = (
        "background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;"
        "padding:1.2rem 0.9rem;text-align:center;height:100%"
    )
    _top_card_style = (
        "background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;"
        "padding:1.2rem 0.9rem;text-align:center;height:100%;"
        "box-shadow:0 2px 8px rgba(0,0,0,0.06)"
    )

    with m1:
        st.markdown(f"""
        <div style="{_top_card_style}">
            <div style="font-size:1.8rem;margin-bottom:0.4rem">🌲</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                        font-size:0.9rem;color:#111827;margin-bottom:0.4rem">Random Forest</div>
            <div style="font-size:0.76rem;color:#6B7280;line-height:1.65">
                100 decision trees · robust to noise · handles non-linear patterns
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style="{_top_card_style}">
            <div style="font-size:1.8rem;margin-bottom:0.4rem">⚡</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                        font-size:0.9rem;color:#111827;margin-bottom:0.4rem">XGBoost</div>
            <div style="font-size:0.76rem;color:#6B7280;line-height:1.65">
                Gradient boosting · high accuracy on tabular data · feature importance
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div style="{_top_card_style}">
            <div style="font-size:1.8rem;margin-bottom:0.4rem">🧬</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                        font-size:0.9rem;color:#111827;margin-bottom:0.4rem">Neural Network</div>
            <div style="font-size:0.76rem;color:#6B7280;line-height:1.65">
                Multi-layer perceptron · captures complex feature interactions
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div style="{_card_style}">
            <div style="font-size:1.8rem;margin-bottom:0.4rem">🎯</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                        font-size:0.9rem;color:#15803D;margin-bottom:0.4rem">Soft Voting Ensemble</div>
            <div style="font-size:0.76rem;color:#374151;line-height:1.65">
                Averages all model probabilities · more stable than any single model
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1rem;padding:0.75rem 1rem;background:#F8FAFC;
                border-radius:10px;font-size:0.8rem;color:#6B7280">
        📥 <strong>Inputs:</strong> Nitrogen · Phosphorus · Potassium · Soil pH · Temperature · Humidity · Rainfall
        &nbsp;→&nbsp;
        📤 <strong>Output:</strong> Ranked crop list with confidence scores
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Dataset ───────────────────────────────────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">📂 Dataset</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:0.7rem">
    """, unsafe_allow_html=True)

    _stats = [
        ("2,200", "Training Records"),
        ("22", "Crop Classes"),
        ("7", "Input Features"),
        ("Kaggle / UCI", "Source"),
    ]
    for val, lbl in _stats:
        st.markdown(f"""
        <div class="ib" style="display:inline-block">
            <div class="ib-l">{lbl}</div>
            <div class="ib-v">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
        <div style="margin-top:0.9rem;font-size:0.8rem;color:#6B7280">
            Features: Nitrogen · Phosphorus · Potassium · Temperature · Humidity · Rainfall · pH
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tech stack ────────────────────────────────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">⚙️ Technology Stack</div>
        <div class="ts-g">
    """, unsafe_allow_html=True)

    _stack = [
        ("🐍", "Python 3.11",   "Core language"),
        ("⚡", "FastAPI",        "Backend REST API"),
        ("🎈", "Streamlit",      "Frontend dashboard"),
        ("🌲", "scikit-learn",   "Random Forest"),
        ("⚡", "XGBoost",        "Gradient boosting"),
        ("🔥", "PyTorch",        "Neural network"),
        ("📊", "Plotly",         "Interactive charts"),
        ("🌤", "Open-Meteo",     "Live weather API"),
        ("🔗", "httpx",          "HTTP client"),
        ("📦", "Render.com",     "Cloud deployment"),
    ]
    for ico, name, desc in _stack:
        st.markdown(f"""
        <div class="ts-i">
            <div class="ts-ico">{ico}</div>
            <strong style="font-size:0.8rem">{name}</strong>
            <br><span style="font-size:0.68rem;color:#9CA3AF">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
