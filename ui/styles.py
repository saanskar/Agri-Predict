"""
AgriPredict — Styles Module  (White Professional Theme)
=========================================================
Single source of truth for all CSS.

Design system
─────────────
  Font:    'Plus Jakarta Sans' (headings) + 'Inter' (body)
  Palette: Clean white/slate background, forest green accent (#16A34A)
  Style:   Modern SaaS dashboard — faculty-friendly, premium, clean
"""

from __future__ import annotations
import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
C_BG            = "#F8FAFC"
C_BG_CARD       = "#FFFFFF"
C_ACCENT        = "#16A34A"
C_ACCENT_MED    = "#22C55E"
C_ACCENT_SOFT   = "#F0FDF4"
C_ACCENT_BORDER = "#BBF7D0"
C_TEXT          = "#111827"
C_TEXT_MED      = "#374151"
C_TEXT_MUTED    = "#6B7280"
C_BORDER        = "#E5E7EB"
C_BORDER_HI     = "#86EFAC"
C_SHADOW        = "rgba(0,0,0,0.06)"
C_SHADOW_MD     = "rgba(0,0,0,0.10)"
MONO            = "'JetBrains Mono', 'Fira Code', monospace"


def inject() -> None:
    """Inject the full CSS into the current Streamlit page."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

    @keyframes fadeUp  {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @keyframes fadeIn  {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
    @keyframes barGrow {{ from {{ width:0; }} }}
    @keyframes float   {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-6px); }} }}
    @keyframes shimmer {{ from {{ background-position:-600px 0; }} to {{ background-position:600px 0; }} }}
    @keyframes pulse   {{ 0%,100% {{ box-shadow:0 0 0 0 rgba(22,163,74,0.0); }} 50% {{ box-shadow:0 0 0 6px rgba(22,163,74,0.12); }} }}

    *, *::before, *::after {{ box-sizing:border-box; }}
    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; color:{C_TEXT}; }}
    #MainMenu, footer, header {{ visibility:hidden; }}

    /* Hide Streamlit auto page navigation */
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    .stApp {{ background:{C_BG} !important; }}
    .main .block-container {{ padding-top:1.8rem !important; max-width:1200px; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background:#FFFFFF !important;
        border-right:1px solid {C_BORDER} !important;
        box-shadow:2px 0 12px {C_SHADOW} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ padding-top:0 !important; }}
    [data-testid="stSidebar"] .stRadio > div {{ gap:2px !important; }}
    [data-testid="stSidebar"] .stRadio label {{
        display:flex !important; align-items:center !important; gap:0.55rem !important;
        padding:0.62rem 1rem !important; border-radius:10px !important; cursor:pointer !important;
        transition:background 0.15s, color 0.15s !important;
        color:{C_TEXT_MED} !important; font-size:0.875rem !important;
        font-weight:500 !important; font-family:'Inter',sans-serif !important;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{ background:{C_ACCENT_SOFT} !important; color:{C_ACCENT} !important; }}

    /* Page header */
    .ph {{ animation:fadeUp 0.38s ease both; margin-bottom:1.6rem; }}
    .ph h1 {{
        font-family:'Plus Jakarta Sans',sans-serif; font-size:clamp(1.5rem,3vw,2rem);
        font-weight:800; color:{C_TEXT}; margin:0 0 0.2rem; letter-spacing:-0.4px;
    }}
    .ph p {{ color:{C_TEXT_MUTED}; font-size:0.875rem; margin:0; }}

    /* White card */
    .gc {{
        background:{C_BG_CARD}; border:1px solid {C_BORDER}; border-radius:16px;
        padding:1.5rem; box-shadow:0 1px 3px {C_SHADOW}, 0 4px 16px rgba(0,0,0,0.04);
        margin-bottom:1.1rem; animation:fadeUp 0.38s ease both;
        position:relative; overflow:hidden; transition:box-shadow 0.2s;
    }}
    .gc:hover {{ box-shadow:0 4px 20px {C_SHADOW_MD}; }}
    .gc::after {{
        content:''; position:absolute; top:0; left:0; right:0; height:3px;
        background:linear-gradient(90deg,{C_ACCENT},{C_ACCENT_MED},#86EFAC);
        border-radius:16px 16px 0 0;
    }}
    .gc-title {{
        font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:0.68rem;
        letter-spacing:1.5px; text-transform:uppercase; color:{C_ACCENT};
        margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;
    }}
    .gc-title::after {{ content:''; flex:1; height:1px; background:{C_BORDER}; }}

    /* KPI grid */
    .kpi-g {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:0.75rem; margin-bottom:1.2rem; }}
    .kpi {{
        background:{C_BG_CARD}; border:1px solid {C_BORDER}; border-radius:14px;
        padding:1.1rem 0.9rem; text-align:center;
        box-shadow:0 1px 3px {C_SHADOW};
        transition:transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        animation:fadeUp 0.38s ease both;
    }}
    .kpi:hover {{ transform:translateY(-3px); box-shadow:0 6px 20px {C_SHADOW_MD}; border-color:{C_ACCENT_BORDER}; }}
    .kpi-ico {{ font-size:1.35rem; margin-bottom:0.3rem; }}
    .kpi-lbl {{ font-size:0.62rem; letter-spacing:1.5px; text-transform:uppercase; color:{C_ACCENT}; margin-bottom:0.22rem; font-weight:600; }}
    .kpi-val {{ font-family:{MONO}; font-size:1.3rem; font-weight:700; color:{C_TEXT}; line-height:1.15; }}
    .kpi-sub {{ font-size:0.65rem; color:{C_TEXT_MUTED}; margin-top:0.15rem; }}

    /* Crop result cards */
    .crc {{
        display:flex; align-items:center; gap:0.7rem; background:{C_BG_CARD};
        border:1px solid {C_BORDER}; border-radius:12px; padding:0.85rem 1rem;
        margin-bottom:0.5rem; box-shadow:0 1px 3px {C_SHADOW};
        transition:transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        animation:fadeUp 0.32s ease both;
    }}
    .crc:hover {{ transform:translateX(4px); border-color:{C_ACCENT_BORDER}; box-shadow:0 4px 14px {C_SHADOW_MD}; }}
    .crc.r1 {{ background:linear-gradient(135deg,{C_ACCENT_SOFT},{C_BG_CARD}); border-color:{C_ACCENT_BORDER}; animation:pulse 3s ease-in-out infinite; }}
    .crc-rank  {{ font-family:{MONO}; font-size:0.8rem; font-weight:700; color:{C_TEXT_MUTED}; min-width:2rem; }}
    .crc-emoji {{ font-size:1.3rem; min-width:2rem; text-align:center; }}
    .crc-info  {{ flex:1; min-width:0; }}
    .crc-name  {{ font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:0.9rem; color:{C_TEXT}; text-transform:capitalize; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .crc-hint  {{ font-size:0.67rem; color:{C_TEXT_MUTED}; margin-top:1px; }}
    .crc-barcol {{ flex:2; min-width:60px; }}
    .crc-barbg  {{ background:{C_ACCENT_SOFT}; border-radius:99px; height:6px; overflow:hidden; margin-bottom:2px; }}
    .crc-fill   {{ height:100%; border-radius:99px; background:linear-gradient(90deg,{C_ACCENT},{C_ACCENT_MED}); animation:barGrow 0.7s cubic-bezier(.4,0,.2,1) both; }}
    .crc-lbl    {{ font-size:0.6rem; color:{C_TEXT_MUTED}; font-family:{MONO}; }}
    .crc-pct    {{ font-family:{MONO}; font-weight:700; font-size:0.88rem; color:{C_ACCENT}; min-width:3rem; text-align:right; }}

    /* Main result banner */
    .mrb {{
        background:linear-gradient(135deg,{C_ACCENT_SOFT} 0%,#DCFCE7 100%);
        border:1px solid {C_ACCENT_BORDER}; border-radius:18px; padding:2rem 1.5rem;
        text-align:center; margin-bottom:1.2rem; position:relative; overflow:hidden;
        animation:fadeUp 0.42s ease both; box-shadow:0 4px 20px rgba(22,163,74,0.08);
    }}
    .mrb::before {{
        content:''; position:absolute; inset:0;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.6),transparent);
        background-size:200% 100%; animation:shimmer 3s linear infinite;
    }}
    .mrb-ico  {{ font-size:3.5rem; display:block; margin-bottom:0.4rem; animation:float 3s ease-in-out infinite; }}
    .mrb-crop {{ font-family:'Plus Jakarta Sans',sans-serif; font-size:1.8rem; font-weight:800; color:{C_TEXT}; text-transform:capitalize; margin-bottom:0.2rem; letter-spacing:-0.4px; }}
    .mrb-conf {{ font-family:{MONO}; font-size:0.9rem; color:{C_ACCENT}; font-weight:600; }}
    .mrb-tags {{ display:flex; justify-content:center; gap:0.4rem; flex-wrap:wrap; margin-top:0.9rem; }}
    .tag {{ display:inline-block; background:#FFFFFF; border:1px solid {C_ACCENT_BORDER}; border-radius:99px; padding:0.2rem 0.75rem; font-size:0.7rem; color:{C_ACCENT}; font-family:'Inter',sans-serif; font-weight:500; box-shadow:0 1px 3px {C_SHADOW}; }}

    /* Weather cards */
    .wg {{ display:grid; grid-template-columns:repeat(3,1fr); gap:0.75rem; margin-bottom:1.1rem; }}
    .wc {{ background:{C_BG_CARD}; border:1px solid {C_BORDER}; border-radius:14px; padding:1.2rem 0.9rem; text-align:center; box-shadow:0 1px 3px {C_SHADOW}; transition:transform 0.2s, box-shadow 0.2s, border-color 0.2s; }}
    .wc:hover {{ transform:translateY(-3px); box-shadow:0 6px 18px {C_SHADOW_MD}; border-color:{C_ACCENT_BORDER}; }}
    .wc-ico  {{ font-size:1.9rem; margin-bottom:0.35rem; }}
    .wc-lbl  {{ font-size:0.62rem; letter-spacing:1.5px; text-transform:uppercase; color:{C_ACCENT}; margin-bottom:0.3rem; font-weight:600; }}
    .wc-val  {{ font-family:{MONO}; font-size:1.5rem; font-weight:700; color:{C_TEXT}; }}
    .wc-unit {{ font-size:0.65rem; color:{C_TEXT_MUTED}; margin-top:2px; }}

    /* Info boxes */
    .ir {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(100px,1fr)); gap:0.6rem; }}
    .ib {{ background:{C_BG}; border:1px solid {C_BORDER}; border-radius:10px; padding:0.75rem 0.65rem; text-align:center; }}
    .ib-l {{ font-size:0.58rem; letter-spacing:1.5px; text-transform:uppercase; color:{C_ACCENT}; margin-bottom:0.2rem; font-weight:600; }}
    .ib-v {{ font-size:0.88rem; font-weight:600; color:{C_TEXT}; }}

    /* Nutrient rows */
    .nr {{ display:flex; align-items:center; gap:0.85rem; padding:0.65rem 0; border-bottom:1px solid {C_BORDER}; }}
    .nr:last-child {{ border-bottom:none; }}
    .nr-name {{ width:100px; font-weight:600; font-size:0.84rem; flex-shrink:0; color:{C_TEXT_MED}; }}
    .nr-bar  {{ flex:1; }}
    .nr-bg   {{ background:{C_ACCENT_SOFT}; border-radius:99px; height:9px; overflow:hidden; }}
    .nr-fill {{ height:100%; border-radius:99px; animation:barGrow 0.7s ease both; }}
    .nr-val  {{ width:70px; text-align:right; font-family:{MONO}; font-size:0.8rem; color:{C_TEXT_MED}; font-weight:600; }}
    .nr-tag  {{ width:68px; text-align:center; font-size:0.68rem; font-weight:700; flex-shrink:0; border-radius:99px; padding:0.15rem 0.35rem; }}

    /* pH scale */
    .ph-scale {{ display:grid; grid-template-columns:repeat(14,1fr); height:26px; border-radius:10px; overflow:hidden; margin-bottom:6px; box-shadow:0 1px 4px {C_SHADOW}; }}
    .ph-seg {{ height:100%; }}
    .ph-ptr {{ font-family:{MONO}; font-size:1.1rem; font-weight:700; color:{C_ACCENT}; text-align:center; margin-top:5px; }}

    /* History rows */
    .hr-row {{ display:flex; align-items:center; gap:0.65rem; padding:0.7rem 0.9rem; background:{C_BG_CARD}; border:1px solid {C_BORDER}; border-radius:10px; margin-bottom:0.4rem; box-shadow:0 1px 3px {C_SHADOW}; transition:border-color 0.15s, box-shadow 0.15s; }}
    .hr-row:hover {{ border-color:{C_ACCENT_BORDER}; box-shadow:0 3px 10px {C_SHADOW_MD}; }}
    .hr-time {{ font-family:{MONO}; font-size:0.7rem; color:{C_TEXT_MUTED}; min-width:80px; }}
    .hr-crop {{ font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:0.86rem; color:{C_TEXT}; text-transform:capitalize; }}
    .hr-conf {{ font-family:{MONO}; font-size:0.78rem; color:{C_ACCENT}; margin-left:auto; font-weight:600; }}

    /* Sidebar logo */
    .sl {{ padding:1.4rem 1rem 1rem; border-bottom:1px solid {C_BORDER}; margin-bottom:0.8rem; }}
    .sl-title {{ font-family:'Plus Jakarta Sans',sans-serif; font-size:1.15rem; font-weight:800; color:{C_TEXT}; display:flex; align-items:center; gap:0.45rem; }}
    .sl-sub {{ font-size:0.62rem; color:{C_TEXT_MUTED}; letter-spacing:1px; margin-top:2px; text-transform:uppercase; }}

    /* Tech stack */
    .ts-g {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(115px,1fr)); gap:0.6rem; }}
    .ts-i {{ background:{C_BG}; border:1px solid {C_BORDER}; border-radius:10px; padding:0.8rem 0.65rem; text-align:center; font-size:0.78rem; color:{C_TEXT_MED}; transition:border-color 0.15s, transform 0.15s, box-shadow 0.15s; box-shadow:0 1px 3px {C_SHADOW}; }}
    .ts-i:hover {{ border-color:{C_ACCENT_BORDER}; transform:translateY(-2px); box-shadow:0 4px 12px {C_SHADOW_MD}; }}
    .ts-ico {{ font-size:1.3rem; margin-bottom:0.3rem; }}

    /* Alerts */
    .alert {{ border-radius:10px; padding:0.8rem 1rem; font-size:0.84rem; line-height:1.55; margin-bottom:0.5rem; border-width:1px; border-style:solid; }}
    .alert-ok     {{ background:#F0FDF4; border-color:#86EFAC; color:#15803D; }}
    .alert-warn   {{ background:#FFFBEB; border-color:#FCD34D; color:#92400E; }}
    .alert-danger {{ background:#FEF2F2; border-color:#FCA5A5; color:#991B1B; }}
    .alert-info   {{ background:#EFF6FF; border-color:#93C5FD; color:#1D4ED8; }}

    /* Widget overrides */
    .stNumberInput label, .stTextInput label, .stSlider label, .stSelectbox label {{
        color:{C_TEXT_MED} !important; font-size:0.84rem !important;
        font-weight:500 !important; font-family:'Inter',sans-serif !important;
    }}
    .stNumberInput input, .stTextInput input {{
        background:{C_BG_CARD} !important; border:1px solid {C_BORDER} !important;
        border-radius:10px !important; color:{C_TEXT} !important;
        font-family:'Inter',sans-serif !important; font-size:0.9rem !important;
        box-shadow:0 1px 2px {C_SHADOW} !important;
        transition:border-color 0.15s, box-shadow 0.15s !important;
    }}
    .stNumberInput input:focus, .stTextInput input:focus {{
        border-color:{C_ACCENT} !important; box-shadow:0 0 0 3px rgba(22,163,74,0.12) !important; outline:none !important;
    }}
    div[data-baseweb="select"] > div {{ background:{C_BG_CARD} !important; border:1px solid {C_BORDER} !important; border-radius:10px !important; color:{C_TEXT} !important; }}
    li[role="option"] {{ background:{C_BG_CARD} !important; color:{C_TEXT} !important; }}
    li[role="option"]:hover {{ background:{C_ACCENT_SOFT} !important; }}

    .stButton > button[kind="primary"] {{
        background:linear-gradient(135deg,{C_ACCENT},{C_ACCENT_MED}) !important;
        border:none !important; border-radius:10px !important; color:#FFFFFF !important;
        font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:700 !important;
        font-size:0.9rem !important; padding:0.65rem 1.5rem !important; width:100%;
        box-shadow:0 4px 14px rgba(22,163,74,0.28) !important;
        transition:transform 0.15s, box-shadow 0.15s !important;
    }}
    .stButton > button[kind="primary"]:hover {{ transform:translateY(-2px) !important; box-shadow:0 8px 24px rgba(22,163,74,0.35) !important; }}
    .stButton > button[kind="secondary"] {{
        background:{C_BG_CARD} !important; border:1px solid {C_BORDER} !important;
        border-radius:10px !important; color:{C_TEXT_MED} !important;
        font-family:'Inter',sans-serif !important; font-weight:500 !important; width:100%;
        box-shadow:0 1px 3px {C_SHADOW} !important; transition:all 0.15s !important;
    }}
    .stButton > button[kind="secondary"]:hover {{ background:{C_ACCENT_SOFT} !important; border-color:{C_ACCENT_BORDER} !important; color:{C_ACCENT} !important; }}

    [data-testid="metric-container"] {{ background:{C_BG_CARD} !important; border:1px solid {C_BORDER} !important; border-radius:12px !important; padding:0.75rem 0.9rem !important; box-shadow:0 1px 3px {C_SHADOW} !important; }}
    [data-testid="stMetricLabel"]   {{ color:{C_TEXT_MUTED} !important; font-size:0.75rem !important; }}
    [data-testid="stMetricValue"]   {{ color:{C_TEXT} !important; font-family:{MONO} !important; }}

    .stSpinner > div {{ border-top-color:{C_ACCENT} !important; }}
    .stAlert {{ border-radius:12px !important; }}
    hr {{ border-color:{C_BORDER} !important; }}
    .streamlit-expanderHeader {{ background:{C_BG} !important; border-radius:10px !important; color:{C_TEXT_MED} !important; font-family:'Inter',sans-serif !important; font-weight:500 !important; }}
    [data-testid="stDownloadButton"] button {{ background:{C_BG_CARD} !important; border:1px solid {C_BORDER} !important; border-radius:10px !important; color:{C_TEXT_MED} !important; font-family:'Inter',sans-serif !important; box-shadow:0 1px 3px {C_SHADOW} !important; transition:all 0.15s !important; }}
    [data-testid="stDownloadButton"] button:hover {{ background:{C_ACCENT_SOFT} !important; border-color:{C_ACCENT_BORDER} !important; color:{C_ACCENT} !important; }}

    /* Mobile */
    @media (max-width: 768px) {{
        .wg {{ grid-template-columns:1fr !important; }}
        .kpi-g {{ grid-template-columns:repeat(2,1fr) !important; }}
        .gc {{ padding:1.1rem 0.9rem !important; }}
        .mrb {{ padding:1.4rem 1rem !important; }}
        .mrb-ico {{ font-size:2.8rem !important; }}
        .mrb-crop {{ font-size:1.4rem !important; }}
        .crc {{ flex-wrap:wrap; gap:0.45rem; }}
        .crc-barcol {{ min-width:100%; order:10; }}
        .ir {{ grid-template-columns:repeat(2,1fr) !important; }}
        .ts-g {{ grid-template-columns:repeat(2,1fr) !important; }}
        .nr {{ flex-wrap:wrap; gap:0.4rem; }}
        .nr-bar {{ min-width:100%; order:10; }}
    }}
    @media (max-width: 480px) {{
        .kpi-g {{ grid-template-columns:1fr 1fr !important; }}
        .ph-scale {{ grid-template-columns:repeat(7,1fr) !important; }}
        .sl-title {{ font-size:1rem !important; }}
        .ph h1 {{ font-size:1.35rem !important; }}
    }}

    /* Mobile hamburger button */
    [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        background: {C_ACCENT} !important;
        border-radius: 10px !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(22,163,74,0.35) !important;
        padding: 0.35rem !important;
        margin: 0.4rem !important;
        position: fixed !important;
        top: 0.5rem !important;
        left: 0.5rem !important;
        z-index: 99999 !important;
    }}
    [data-testid="collapsedControl"] svg {{
        fill: white !important;
        stroke: white !important;
    }}

    /* Mobile top nav dropdown */
    .mobile-nav {{ display: none; }}

    @media (max-width: 768px) {{
        .mobile-nav {{
            display: block !important;
            position: sticky;
            top: 0;
            z-index: 1000;
            background: {C_BG_CARD};
            padding: 0.5rem 0.5rem 0.4rem;
            border-bottom: 1px solid {C_BORDER};
            box-shadow: 0 2px 8px {C_SHADOW};
            margin-bottom: 0.8rem;
        }}
        .mobile-nav .stSelectbox {{ margin: 0 !important; }}
        .mobile-nav .stSelectbox > div > div {{
            background: {C_ACCENT_SOFT} !important;
            border: 1.5px solid {C_ACCENT} !important;
            border-radius: 10px !important;
            color: {C_ACCENT} !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }}
        [data-testid="stSidebar"] {{ display: none !important; }}
        .main .block-container {{
            padding-top: 0.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }}
        .stButton > button {{
            min-height: 48px !important;
            font-size: 1rem !important;
        }}
        [data-testid="column"] {{ min-width: 100% !important; }}
    }}
    
    </style>
    """, unsafe_allow_html=True)
