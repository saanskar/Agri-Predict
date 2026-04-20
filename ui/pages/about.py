"""
AgriPredict — About Page
"""
from __future__ import annotations
import streamlit as st


def _card(ico: str, title: str, desc: str, green: bool = False) -> str:
    bg  = "#F0FDF4" if green else "#FFFFFF"
    bdr = "#BBF7D0" if green else "#E5E7EB"
    tc  = "#15803D" if green else "#111827"
    return f"""
    <div style="background:{bg};border:1px solid {bdr};border-radius:14px;
                padding:1.2rem 0.9rem;text-align:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);margin-bottom:0.5rem">
        <div style="font-size:1.8rem;margin-bottom:0.5rem">{ico}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                    font-size:0.88rem;color:{tc};margin-bottom:0.35rem">{title}</div>
        <div style="font-size:0.74rem;color:#6B7280;line-height:1.6">{desc}</div>
    </div>"""


def _stat(val: str, lbl: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                padding:1rem 0.8rem;text-align:center;margin-bottom:0.5rem">
        <div style="font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;
                    color:#16A34A;font-weight:600;margin-bottom:0.3rem">{lbl}</div>
        <div style="font-size:1rem;font-weight:700;color:#111827">{val}</div>
    </div>"""


def _tech(ico: str, name: str, desc: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                padding:0.9rem 0.7rem;text-align:center;margin-bottom:0.5rem;
                box-shadow:0 1px 3px rgba(0,0,0,0.05)">
        <div style="font-size:1.3rem;margin-bottom:0.3rem">{ico}</div>
        <div style="font-size:0.8rem;font-weight:600;color:#111827">{name}</div>
        <div style="font-size:0.68rem;color:#9CA3AF;margin-top:2px">{desc}</div>
    </div>"""


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>📖 About AgriPredict</h1>
        <p>AI-driven crop recommendation system combining soil analysis with real-time weather</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Overview ──────────────────────────────────────────────────
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
            Network — whose predictions are averaged for higher accuracy than any single model alone.
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
            <div style="font-size:0.87rem;color:#374151;line-height:2.1">
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
            <div style="font-size:0.87rem;color:#374151;line-height:2.1">
                🤖 Ensemble model: RF + XGBoost + Neural Net<br>
                🌦️ Live weather via Open-Meteo API<br>
                🧪 NPK + pH as direct model features<br>
                📍 GPS-enabled — works from any location<br>
                📱 Mobile-friendly, browser-based
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── ML Architecture — responsive grid via HTML ────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">🧠 Machine Learning Architecture</div>
        <div style="display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:0.75rem;">
            <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;
                        padding:1.2rem 0.9rem;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05)">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">🌲</div>
                <div style="font-weight:700;font-size:0.88rem;color:#111827;margin-bottom:0.35rem">Random Forest</div>
                <div style="font-size:0.74rem;color:#6B7280;line-height:1.6">100 decision trees · robust to noise · non-linear patterns</div>
            </div>
            <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;
                        padding:1.2rem 0.9rem;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05)">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">⚡</div>
                <div style="font-weight:700;font-size:0.88rem;color:#111827;margin-bottom:0.35rem">XGBoost</div>
                <div style="font-size:0.74rem;color:#6B7280;line-height:1.6">Gradient boosting · high accuracy · feature importance</div>
            </div>
            <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;
                        padding:1.2rem 0.9rem;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05)">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">🧬</div>
                <div style="font-weight:700;font-size:0.88rem;color:#111827;margin-bottom:0.35rem">Neural Network</div>
                <div style="font-size:0.74rem;color:#6B7280;line-height:1.6">Multi-layer perceptron · captures complex interactions</div>
            </div>
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;
                        padding:1.2rem 0.9rem;text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05)">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">🎯</div>
                <div style="font-weight:700;font-size:0.88rem;color:#15803D;margin-bottom:0.35rem">Soft Voting Ensemble</div>
                <div style="font-size:0.74rem;color:#374151;line-height:1.6">Averages all probabilities · more stable than single models</div>
            </div>
        </div>
        <div style="margin-top:1rem;padding:0.75rem 1rem;background:#F8FAFC;
                    border-radius:10px;font-size:0.8rem;color:#6B7280">
            📥 <strong>Inputs:</strong>
            Nitrogen · Phosphorus · Potassium · Soil pH · Temperature · Humidity · Rainfall
            &nbsp;→&nbsp;
            📤 <strong>Output:</strong> Ranked crop list with confidence scores
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Dataset — responsive grid via HTML ────────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">📂 Dataset</div>
        <div style="display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:0.75rem;margin-bottom:0.9rem">
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:1rem 0.8rem;text-align:center">
                <div style="font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;
                            color:#16A34A;font-weight:600;margin-bottom:0.3rem">Training Records</div>
                <div style="font-size:1rem;font-weight:700;color:#111827">2,200</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:1rem 0.8rem;text-align:center">
                <div style="font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;
                            color:#16A34A;font-weight:600;margin-bottom:0.3rem">Crop Classes</div>
                <div style="font-size:1rem;font-weight:700;color:#111827">22</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:1rem 0.8rem;text-align:center">
                <div style="font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;
                            color:#16A34A;font-weight:600;margin-bottom:0.3rem">Input Features</div>
                <div style="font-size:1rem;font-weight:700;color:#111827">7</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:1rem 0.8rem;text-align:center">
                <div style="font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;
                            color:#16A34A;font-weight:600;margin-bottom:0.3rem">Source</div>
                <div style="font-size:1rem;font-weight:700;color:#111827">Kaggle / UCI</div>
            </div>
        </div>
        <div style="font-size:0.8rem;color:#6B7280">
            Features: Nitrogen · Phosphorus · Potassium · Temperature · Humidity · Rainfall · pH
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tech Stack — responsive grid via HTML ─────────────────────
    st.markdown("""
    <div class="gc">
        <div class="gc-title">⚙️ Technology Stack</div>
        <div style="display:grid;
                    grid-template-columns:repeat(5,1fr);
                    gap:0.65rem">
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🐍</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">Python 3.11</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Core language</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">⚡</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">FastAPI</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Backend API</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🎈</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">Streamlit</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Frontend</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🌲</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">scikit-learn</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Random Forest</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">⚡</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">XGBoost</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Boosting</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🔥</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">PyTorch</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Neural Net</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">📊</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">Plotly</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Charts</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🌤</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">Open-Meteo</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Weather API</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">🔗</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">httpx</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">HTTP client</div>
            </div>
            <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;
                        padding:0.9rem 0.5rem;text-align:center">
                <div style="font-size:1.3rem;margin-bottom:0.3rem">📦</div>
                <div style="font-size:0.78rem;font-weight:600;color:#111827">Render.com</div>
                <div style="font-size:0.65rem;color:#9CA3AF;margin-top:2px">Deployment</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)