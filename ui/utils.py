"""
AgriPredict — Utils Module
===========================
Centralises:
  • API communication with the V1 FastAPI backend
  • Session-state initialisation
  • Crop metadata (emoji, water, yield, profitability)
  • Soil health heuristics
  • History helpers
  • Error types

Never import Streamlit here; this module is pure Python so it stays
unit-testable.
"""

from __future__ import annotations

import csv
import io
import os
from datetime import datetime
from typing import Any

import httpx


# ── Backend URL ──────────────────────────────────────────────────────────────
API_BASE = os.environ.get(
    "AGRIPREDICT_API_BASE_URL",
    "https://agri-predict-v4em.onrender.com",
).rstrip("/")

_TIMEOUT = 60.0


# ── Custom exceptions ─────────────────────────────────────────────────────────

class APIError(Exception):
    """Raised when the AgriPredict backend returns a non-2xx status."""
    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"API {status}: {detail}")


class NetworkError(Exception):
    """Raised on connection / timeout failures before receiving a response."""


# ── Crop metadata ─────────────────────────────────────────────────────────────

CROP_META: dict[str, dict[str, str]] = {
    "rice":          {"emoji": "🌾", "water": "High",    "yield": "4–6 t/ha",    "profit": "Medium"},
    "wheat":         {"emoji": "🌾", "water": "Medium",  "yield": "3–5 t/ha",    "profit": "Medium"},
    "maize":         {"emoji": "🌽", "water": "Medium",  "yield": "5–8 t/ha",    "profit": "High"},
    "corn":          {"emoji": "🌽", "water": "Medium",  "yield": "5–8 t/ha",    "profit": "High"},
    "cotton":        {"emoji": "🌿", "water": "Medium",  "yield": "2–4 t/ha",    "profit": "High"},
    "sugarcane":     {"emoji": "🎋", "water": "High",    "yield": "60–80 t/ha",  "profit": "High"},
    "jute":          {"emoji": "🌱", "water": "High",    "yield": "2–3 t/ha",    "profit": "Low"},
    "coffee":        {"emoji": "☕", "water": "Medium",  "yield": "0.5–1 t/ha",  "profit": "Very High"},
    "banana":        {"emoji": "🍌", "water": "High",    "yield": "20–30 t/ha",  "profit": "Medium"},
    "mango":         {"emoji": "🥭", "water": "Low",     "yield": "8–12 t/ha",   "profit": "High"},
    "grapes":        {"emoji": "🍇", "water": "Medium",  "yield": "10–20 t/ha",  "profit": "Very High"},
    "watermelon":    {"emoji": "🍉", "water": "Medium",  "yield": "20–30 t/ha",  "profit": "Medium"},
    "apple":         {"emoji": "🍎", "water": "Medium",  "yield": "15–25 t/ha",  "profit": "High"},
    "orange":        {"emoji": "🍊", "water": "Medium",  "yield": "15–25 t/ha",  "profit": "High"},
    "papaya":        {"emoji": "🍈", "water": "Medium",  "yield": "30–40 t/ha",  "profit": "Medium"},
    "pomegranate":   {"emoji": "🍎", "water": "Low",     "yield": "8–12 t/ha",   "profit": "Very High"},
    "coconut":       {"emoji": "🥥", "water": "Medium",  "yield": "5–8 t/ha",    "profit": "Medium"},
    "chickpea":      {"emoji": "🫘", "water": "Low",     "yield": "1–2 t/ha",    "profit": "Medium"},
    "lentil":        {"emoji": "🫘", "water": "Low",     "yield": "1–2 t/ha",    "profit": "Medium"},
    "mungbean":      {"emoji": "🫘", "water": "Low",     "yield": "1–2 t/ha",    "profit": "Low"},
    "blackgram":     {"emoji": "🫘", "water": "Low",     "yield": "0.8–1.5 t/ha","profit": "Low"},
    "kidney beans":  {"emoji": "🫘", "water": "Medium",  "yield": "1–2 t/ha",    "profit": "Medium"},
    "moth beans":    {"emoji": "🫘", "water": "Low",     "yield": "0.5–1 t/ha",  "profit": "Low"},
    "pigeonpeas":    {"emoji": "🫘", "water": "Low",     "yield": "1–2 t/ha",    "profit": "Low"},
    "soybean":       {"emoji": "🫛", "water": "Medium",  "yield": "2–3 t/ha",    "profit": "High"},
}
_DEFAULT_META: dict[str, str] = {"emoji": "🌿", "water": "Medium", "yield": "Varies", "profit": "Medium"}


def crop_meta(name: str) -> dict[str, str]:
    return CROP_META.get(name.lower().strip(), _DEFAULT_META)


def crop_emoji(name: str) -> str:
    return crop_meta(name)["emoji"]


# ── Session state defaults ─────────────────────────────────────────────────────

DEFAULTS: dict[str, Any] = {
    "lat":         20.0,
    "lon":         78.0,
    "n":           50.0,
    "p":           40.0,
    "k":           40.0,
    "ph":          6.5,
    "top_k":       5,
    "last_result": None,   # full API response dict
    "last_weather":None,   # weather sub-dict
    "history":     [],     # list[dict]
    "request_geo": False,
    "api_error":   None,   # last error string | None
}


def init_session(st_module: Any) -> None:
    """Call once at app startup.  st_module is the imported streamlit module."""
    for k, v in DEFAULTS.items():
        if k not in st_module.session_state:
            st_module.session_state[k] = v


# ── API call ──────────────────────────────────────────────────────────────────

def call_recommendations(
    lat: float, lon: float,
    n: float, p: float, k: float, ph: float,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    POST /recommendations to the V1 FastAPI backend.

    Returns the parsed JSON response dict on success.
    Raises:
        APIError     — non-2xx HTTP status
        NetworkError — connection / timeout
    """
    payload: dict[str, Any] = {
        "location": {"lat": lat, "lon": lon},
        "soil":     {"n": n, "p": p, "k": k, "ph": ph},
        "top_k":    top_k,
    }
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(f"{API_BASE}/recommendations", json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
        raise NetworkError(str(exc)) from exc
    except Exception as exc:
        raise NetworkError(f"Unexpected transport error: {exc}") from exc

    if not resp.is_success:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise APIError(resp.status_code, str(detail))

    try:
        return resp.json()
    except Exception as exc:
        raise NetworkError(f"Could not parse API response: {exc}") from exc


def check_api_health() -> bool:
    """Returns True if the backend /health endpoint responds OK."""
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(f"{API_BASE}/health")
            return resp.status_code == 200
    except Exception:
        return False


# ── History helpers ───────────────────────────────────────────────────────────

def push_history(
    st_module: Any,
    n: float, p: float, k: float, ph: float,
    lat: float, lon: float,
    recommendations: list[dict[str, Any]],
    weather: dict[str, Any],
) -> None:
    """Prepend a prediction record to session history (capped at 50)."""
    if not recommendations:
        return
    top = recommendations[0]
    record: dict[str, Any] = {
        "ts":         datetime.now().isoformat(timespec="seconds"),
        "date":       datetime.now().strftime("%d %b %Y"),
        "time":       datetime.now().strftime("%H:%M:%S"),
        "n": n, "p": p, "k": k, "ph": ph,
        "lat": lat, "lon": lon,
        "crop":       top.get("crop", ""),
        "confidence": float(top.get("probability", 0.0)),
        "weather":    weather,
        "all_recs":   recommendations,
    }
    st_module.session_state.history = (
        [record] + st_module.session_state.history
    )[:50]


def history_to_csv(history: list[dict[str, Any]]) -> str:
    """Serialise the history list to a CSV string for download."""
    buf = io.StringIO()
    cols = ["date", "time", "crop", "confidence", "n", "p", "k", "ph", "lat", "lon"]
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    for row in history:
        writer.writerow({**row, "confidence": f"{row['confidence']*100:.2f}%"})
    return buf.getvalue()


# ── Soil heuristics ───────────────────────────────────────────────────────────

def soil_score(n: float, p: float, k: float, ph: float) -> int:
    """
    0–100 heuristic soil health index.
    40-120 / 30-100 / 30-100 for N/P/K, 5.5-7.5 for pH are the ideal bands.
    """
    def _band(v: float, lo: float, hi: float, ok: int, near: int, far: int) -> int:
        if lo <= v <= hi:
            return ok
        half = (hi - lo) * 0.5
        if lo - half <= v <= hi + half:
            return near
        return far

    return min(100,
        _band(n,  40, 120, 30, 18, 5) +
        _band(p,  30, 100, 25, 14, 4) +
        _band(k,  30, 100, 25, 14, 4) +
        _band(ph, 5.5, 7.5, 20, 12, 3)
    )


def soil_tips(n: float, p: float, k: float, ph: float) -> list[tuple[str, str]]:
    """
    Returns list of (message, level) where level ∈ {'ok', 'warn', 'danger'}.
    """
    tips: list[tuple[str, str]] = []

    if n < 20:
        tips.append(("⚠️ Nitrogen very low — apply urea or DAP fertiliser urgently.", "danger"))
    elif n < 40:
        tips.append(("💡 Nitrogen slightly low — add compost or ammonium sulphate.", "warn"))
    elif n > 180:
        tips.append(("⚠️ Nitrogen excess — may cause leaf burn; reduce N inputs.", "warn"))
    else:
        tips.append(("✅ Nitrogen level is adequate.", "ok"))

    if p < 15:
        tips.append(("⚠️ Phosphorus very low — apply SSP or rock phosphate.", "danger"))
    elif p < 30:
        tips.append(("💡 Phosphorus slightly low — add bone meal or DAP.", "warn"))
    else:
        tips.append(("✅ Phosphorus level is adequate.", "ok"))

    if k < 15:
        tips.append(("⚠️ Potassium very low — apply MOP or wood ash.", "danger"))
    elif k < 30:
        tips.append(("💡 Potassium slightly low — consider potash fertiliser.", "warn"))
    else:
        tips.append(("✅ Potassium level is adequate.", "ok"))

    if ph < 5.0:
        tips.append(("⚠️ Very acidic soil (pH < 5) — apply agricultural lime.", "danger"))
    elif ph < 5.5:
        tips.append(("💡 Mildly acidic — dolomite lime can raise pH gradually.", "warn"))
    elif ph > 8.0:
        tips.append(("⚠️ Highly alkaline (pH > 8) — apply elemental sulphur.", "danger"))
    elif ph > 7.5:
        tips.append(("💡 Slightly alkaline — watch micronutrient availability.", "warn"))
    else:
        tips.append(("✅ Soil pH is in the ideal range.", "ok"))

    return tips


# ── Irrigation advice ─────────────────────────────────────────────────────────

def irrigation_advice(rainfall_mm: float) -> tuple[str, str]:
    """
    Returns (message, level) based on rainfall.
    Level ∈ {'ok', 'warn', 'danger', 'info'}.
    """
    r = rainfall_mm
    if r == 0:
        return ("☀️ No rainfall recorded — irrigation is essential.", "danger")
    if r < 5:
        return ("🌦 Very light rainfall (<5 mm) — supplemental irrigation required.", "warn")
    if r < 15:
        return ("🌧 Moderate rainfall — monitor soil moisture before irrigating.", "info")
    if r < 30:
        return ("🌧 Adequate rainfall — irrigation likely not needed today.", "ok")
    return ("⛈ Heavy rainfall (>30 mm) — avoid irrigation; ensure proper drainage.", "warn")
