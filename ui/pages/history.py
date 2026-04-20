"""
AgriPredict — Prediction History Page
=======================================
Stores and displays every prediction made in the current browser session.
All values are real — sourced from the V1 API response stored in
session_state by the Predict page.

Features:
  • Summary KPIs (total, avg confidence, unique crops)
  • Real confidence trend line chart
  • Expandable prediction records with all recommendations
  • CSV download
  • Clear history button
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from charts import history_trend
from utils  import crop_emoji, history_to_csv


def render() -> None:
    st.markdown("""
    <div class="ph">
        <h1>📋 Prediction History</h1>
        <p>Every crop prediction you've made this session — real data from the backend</p>
    </div>
    """, unsafe_allow_html=True)

    history: list[dict[str, Any]] = st.session_state.history

    # ── Empty state ───────────────────────────────────────────────
    if not history:
        st.markdown("""
        <div class="gc" style="text-align:center;padding:3.5rem 1rem">
            <div style="font-size:3.5rem;margin-bottom:0.9rem">📋</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1.1rem;
                        color:#111827;margin-bottom:0.4rem">No history yet</div>
            <div style="font-size:0.86rem;color:#6B7280">
                Make a prediction on the <strong>Predict Crop</strong> page.
                Every result is saved here automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Summary KPIs ──────────────────────────────────────────────
    total      = len(history)
    avg_conf   = sum(h["confidence"] for h in history) / total
    crops_seen = list(dict.fromkeys(h["crop"] for h in history))
    best       = max(history, key=lambda h: h["confidence"])

    st.markdown(f"""
    <div class="kpi-g" style="grid-template-columns:repeat(4,1fr)">
        <div class="kpi">
            <div class="kpi-ico">📊</div>
            <div class="kpi-lbl">Predictions</div>
            <div class="kpi-val">{total}</div>
        </div>
        <div class="kpi">
            <div class="kpi-ico">🎯</div>
            <div class="kpi-lbl">Avg Confidence</div>
            <div class="kpi-val">{avg_conf*100:.1f}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-ico">🌾</div>
            <div class="kpi-lbl">Unique Crops</div>
            <div class="kpi-val">{len(crops_seen)}</div>
        </div>
        <div class="kpi">
            <div class="kpi-ico">{crop_emoji(best['crop'])}</div>
            <div class="kpi-lbl">Best Result</div>
            <div class="kpi-val" style="font-size:0.95rem">{best['crop'].title()}</div>
            <div class="kpi-sub">{best['confidence']*100:.1f}% confidence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Confidence trend chart ─────────────────────────────────────
    if total >= 2:
        st.markdown('<div class="gc"><div class="gc-title">📈 Confidence Trend (Real)</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(history_trend(history), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Export + Clear controls ────────────────────────────────────
    top_r, exp_r = st.columns([3, 1])
    with top_r:
        st.markdown('<div class="gc-title" style="margin-bottom:0.8rem">🕒 Prediction Records</div>',
                    unsafe_allow_html=True)
    with exp_r:
        st.download_button(
            "⬇️ Export CSV",
            data=history_to_csv(history),
            file_name="agripredict_history.csv",
            mime="text/csv",
            key="dl_csv",
        )

    # ── Records ───────────────────────────────────────────────────
    st.markdown('<div class="gc">', unsafe_allow_html=True)

    for i, rec in enumerate(history):
        emoji   = crop_emoji(rec["crop"])
        conf    = rec["confidence"] * 100
        w       = rec.get("weather", {})
        temp    = w.get("temperature_c")
        rain    = w.get("rainfall_mm", 0.0)
        temp_s  = f"🌡️ {temp:.0f}°C  " if temp is not None else ""
        rain_s  = f"🌧️ {rain:.0f} mm" if rain else ""

        with st.expander(
            f"{emoji} {rec['crop'].title()}  —  {conf:.1f}%  ·  {rec['date']} {rec['time']}",
            expanded=(i == 0),
        ):
            s_l, s_r = st.columns(2)
            with s_l:
                st.markdown(f"""
                <div class="ir" style="margin:0">
                    <div class="ib"><div class="ib-l">N</div><div class="ib-v">{rec['n']:.0f}</div></div>
                    <div class="ib"><div class="ib-l">P</div><div class="ib-v">{rec['p']:.0f}</div></div>
                    <div class="ib"><div class="ib-l">K</div><div class="ib-v">{rec['k']:.0f}</div></div>
                    <div class="ib"><div class="ib-l">pH</div><div class="ib-v">{rec['ph']:.1f}</div></div>
                </div>
                """, unsafe_allow_html=True)
            with s_r:
                st.markdown(f"""
                <div style="font-size:0.82rem;color:#374151;line-height:2.1">
                    📍 {rec['lat']:.3f}°, {rec['lon']:.3f}°<br>
                    {temp_s}{rain_s}
                </div>
                """, unsafe_allow_html=True)

            # All recommendations for this entry
            all_recs = rec.get("all_recs", [])
            if all_recs:
                for j, r in enumerate(all_recs[:5], 1):
                    r_pct = float(r["probability"]) * 100
                    c_icon = "🥇" if j==1 else "🥈" if j==2 else "🥉" if j==3 else f"#{j}"
                    conf_c = "#3ddc84" if j == 1 else "#80f5b8"
                    st.markdown(f"""
                    <div class="hr-row">
                        <span style="min-width:1.5rem;font-size:0.78rem">{c_icon}</span>
                        <span style="font-size:1rem">{crop_emoji(r['crop'])}</span>
                        <span class="hr-crop">{r['crop'].title()}</span>
                        <div style="flex:1;margin:0 0.8rem">
                            <div class="crc-barbg" style="height:5px">
                                <div class="crc-fill" style="width:{r_pct:.0f}%"></div>
                            </div>
                        </div>
                        <span class="hr-conf" style="color:{conf_c}">{r_pct:.1f}%</span>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Clear ──────────────────────────────────────────────────────
    if st.button("🗑️ Clear All History", key="clr_hist"):
        st.session_state.history = []
        st.success("History cleared.")
        st.rerun()
