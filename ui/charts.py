"""
AgriPredict — Charts Module
============================
All Plotly figures used across the dashboard.

Design rules
────────────
• Paper and plot backgrounds are transparent (rgba(0,0,0,0)) so they
  sit flush inside the glass cards.
• Colour palette matches styles.py design tokens.
• Every function returns a go.Figure; caller passes to st.plotly_chart().
• No fake / simulated data is generated here — callers supply real values.
"""

from __future__ import annotations

import math
from typing import Any

import plotly.graph_objects as go


# ── Design tokens (must match styles.py) ──────────────────────────────────────
_C_ACCENT  = "#16A34A"
_C_DIM     = "#22C55E"
_C_SOFT    = "#86EFAC"
_C_MUTED   = "#6B7280"
_C_GRID    = "#F3F4F6"
_C_ZERO    = "#E5E7EB"
_FONT      = "Plus Jakarta Sans, Inter, sans-serif"
_MONO      = "JetBrains Mono, Fira Code, monospace"

_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family=_FONT, color="#374151", size=11),
    margin=dict(l=12, r=12, t=28, b=12),
)
_AXIS = dict(gridcolor=_C_GRID, zerolinecolor=_C_ZERO, linecolor="rgba(0,0,0,0)")


def _cs(values: list[float]) -> list[float]:
    """Normalise a list to [0,1] for colorscale mapping."""
    mn, mx = min(values, default=0), max(values, default=1)
    span = mx - mn or 1
    return [(v - mn) / span for v in values]


_GREEN_SCALE = [
    [0.0, "#86EFAC"],
    [0.5, "#22C55E"],
    [1.0, "#15803D"],
]


# ── 1. NPK horizontal bar chart ───────────────────────────────────────────────

def npk_bar(n: float, p: float, k: float) -> go.Figure:
    """
    Horizontal grouped bars: user values vs ideal midpoint.
    Ideal ranges: N 40–120, P 30–100, K 30–100.
    """
    labels   = ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"]
    vals     = [n, p, k]
    ideals   = [80, 65, 65]
    colours  = [_C_ACCENT, _C_DIM, _C_SOFT]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Your Soil",
        x=vals, y=labels, orientation="h",
        marker=dict(color=colours, opacity=0.88,
                    line=dict(color="rgba(61,220,132,0.45)", width=1)),
        text=[f"{v:.0f} kg/ha" for v in vals],
        textposition="outside",
        textfont=dict(size=10, family=_MONO, color="#374151"),
        cliponaxis=False,
        hovertemplate="%{y}: <b>%{x:.0f} kg/ha</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="Ideal midpoint",
        x=ideals, y=labels, mode="markers",
        marker=dict(symbol="line-ns-open", size=20,
                    color="rgba(245,200,66,0.75)",
                    line=dict(width=2.5)),
        hovertemplate="%{y} ideal: <b>%{x} kg/ha</b><extra></extra>",
    ))
    fig.update_layout(
        **_BASE,
        barmode="group", height=210,
        xaxis=dict(**_AXIS, title="kg / ha",
                   range=[0, max(vals + ideals + [1]) * 1.45]),
        yaxis=dict(**_AXIS),
        legend=dict(orientation="h", y=1.12, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )
    return fig


# ── 2. Crop radar / polar bar ─────────────────────────────────────────────────

def crop_radar(recs: list[dict[str, Any]], top_n: int = 5) -> go.Figure:
    """Polar bar chart showing top-N crop confidence scores."""
    show   = recs[:top_n]
    names  = [r["crop"].title() for r in show]
    probs  = [float(r["probability"]) * 100 for r in show]

    fig = go.Figure(go.Barpolar(
        r=probs, theta=names,
        marker=dict(
            color=probs,
            colorscale=_GREEN_SCALE,
            line=dict(color="rgba(61,220,132,0.42)", width=1),
        ),
        hovertemplate="<b>%{theta}</b><br>Confidence: %{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **_BASE, height=320, showlegend=False,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(tickcolor="rgba(61,220,132,0.35)",
                             linecolor="rgba(61,220,132,0.18)"),
            radialaxis=dict(range=[0, 100], ticksuffix="%",
                            gridcolor=_C_GRID,
                            linecolor="rgba(61,220,132,0.18)"),
        ),
    )
    return fig


# ── 3. Confidence vertical bar chart ──────────────────────────────────────────

def confidence_bars(recs: list[dict[str, Any]]) -> go.Figure:
    """Vertical bar chart of all returned crop confidence scores."""
    crops = [r["crop"].title() for r in recs]
    probs = [float(r["probability"]) * 100 for r in recs]

    fig = go.Figure(go.Bar(
        x=crops, y=probs,
        marker=dict(color=probs, colorscale=_GREEN_SCALE,
                    line=dict(color="rgba(61,220,132,0.3)", width=1)),
        text=[f"{p:.1f}%" for p in probs],
        textposition="outside",
        textfont=dict(size=9, family=_MONO),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **_BASE, height=250,
        xaxis=dict(**_AXIS, tickfont=dict(size=10)),
        yaxis=dict(**_AXIS, title="Confidence (%)",
                   range=[0, max(probs, default=100) * 1.22]),
    )
    return fig


# ── 4. Soil health gauge ──────────────────────────────────────────────────────

def soil_gauge(score: int) -> go.Figure:
    """Speedometer gauge for the 0–100 soil health score."""
    colour = (
        _C_ACCENT        if score >= 75 else
        "#f5c842"        if score >= 50 else
        "#F97316"        if score >= 25 else
        "#f55a5a"
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain=dict(x=[0, 1], y=[0, 1]),
        title=dict(text="Soil Health Score", font=dict(size=13, color="#8be8b8")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1,
                      tickcolor="rgba(61,220,132,0.4)",
                      tickfont=dict(color="#8be8b8", size=9)),
            bar=dict(color=colour, thickness=0.24),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=1, bordercolor="rgba(61,220,132,0.28)",
            steps=[
                dict(range=[0,  25], color="rgba(254,202,202,0.5)"),
                dict(range=[25, 50], color="rgba(253,230,138,0.4)"),
                dict(range=[50, 75], color="rgba(253,224,71,0.3)"),
                dict(range=[75,100], color="rgba(134,239,172,0.3)"),
            ],
            threshold=dict(
                line=dict(color="rgba(255,255,255,0.45)", width=2),
                thickness=0.72, value=60,
            ),
        ),
        number=dict(font=dict(size=30, color="#80f5b8", family=_MONO)),
    ))
    fig.update_layout(**_BASE, height=220)
    return fig


# ── 5. pH colour scale (HTML helper) ─────────────────────────────────────────

def ph_scale_html(ph: float) -> str:
    """
    Returns a raw HTML string rendering a 14-segment pH colour scale
    with the current pH value pointer.
    """
    _colours = [
        "#ff2e2e","#ff5500","#ff7700","#ffaa00","#ffcc00",
        "#d8e000","#a0cc00","#3ddc84","#00b894","#0099cc",
        "#0066cc","#0044bb","#2222aa","#3311aa",
    ]
    segs = ""
    for i, c in enumerate(_colours, 1):
        active = abs(ph - i) < 0.65
        opacity = "1" if active else "0.28"
        segs += (
            f'<div class="ph-seg" '
            f'style="background:{c};opacity:{opacity};" title="pH {i}"></div>'
        )
    ptr_pct = max(0, min(96, (ph / 14) * 100))
    return f"""
    <div style="font-size:0.62rem;color:rgba(61,220,132,0.5);
                display:flex;justify-content:space-between;margin-bottom:4px">
        <span>Acidic (0)</span><span>Neutral (7)</span><span>Alkaline (14)</span>
    </div>
    <div style="position:relative;">
        <div class="ph-scale">{segs}</div>
        <div style="position:absolute;top:-9px;left:{ptr_pct}%;
                    transform:translateX(-50%);font-size:0.95rem;color:#3ddc84">▼</div>
    </div>
    <div class="ph-ptr">pH = {ph:.1f}</div>
    """


# ── 6. Weather trend from real data points ────────────────────────────────────

def weather_sparkline(
    temperatures: list[float],
    humidities: list[float],
    labels: list[str],
) -> go.Figure:
    """
    Multi-axis line chart for real weather readings over time.
    Called with whatever time-series data is available.
    Falls back gracefully to a single data point (shown as scatter).
    """
    mode = "lines+markers" if len(temperatures) > 1 else "markers"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=temperatures, name="Temperature (°C)",
        mode=mode,
        line=dict(color="#F97316", width=2.5, shape="spline"),
        marker=dict(size=8, color="#F97316"),
        fill="tozeroy" if len(temperatures) > 1 else None,
        fillcolor="rgba(245,160,66,0.05)",
        yaxis="y1",
        hovertemplate="%{y:.1f}°C<extra>Temperature</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=humidities, name="Humidity (%)",
        mode=mode,
        line=dict(color=_C_ACCENT, width=2.5, shape="spline"),
        marker=dict(size=8, color=_C_ACCENT),
        fill="tozeroy" if len(humidities) > 1 else None,
        fillcolor="rgba(61,220,132,0.05)",
        yaxis="y2",
        hovertemplate="%{y:.1f}%<extra>Humidity</extra>",
    ))
    fig.update_layout(
        **_BASE, height=260,
        xaxis=dict(**_AXIS),
        yaxis=dict(**_AXIS, title="Temp (°C)", side="left",  color="#F97316"),
        yaxis2=dict(title="Humidity (%)", side="right",
            overlaying="y", color=_C_ACCENT,
            gridcolor="rgba(0,0,0,0)",
            zerolinecolor="rgba(0,0,0,0)",
            linecolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", y=1.12, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )
    return fig


# ── 7. History confidence trend ────────────────────────────────────────────────

def history_trend(history: list[dict[str, Any]]) -> go.Figure:
    """Line chart showing prediction confidence across history records."""
    if not history:
        return go.Figure()
    # history is stored newest-first; reverse for chronological display
    ordered = list(reversed(history))
    labels  = [f"#{i+1}" for i in range(len(ordered))]
    confs   = [h["confidence"] * 100 for h in ordered]
    crops   = [h["crop"].title() for h in ordered]

    fig = go.Figure(go.Scatter(
        x=labels, y=confs,
        mode="lines+markers",
        line=dict(color=_C_ACCENT, width=2.5, shape="spline"),
        marker=dict(size=8, color=_C_ACCENT,
                    line=dict(color=_C_SOFT, width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(61,220,132,0.06)",
        hovertext=[f"{c} — {v:.1f}%" for c, v in zip(crops, confs)],
        hovertemplate="%{hovertext}<extra></extra>",
    ))
    fig.update_layout(
        **_BASE, height=200,
        xaxis=dict(**_AXIS, title="Prediction #"),
        yaxis=dict(**_AXIS, title="Confidence (%)", range=[0, 105]),
    )
    return fig
