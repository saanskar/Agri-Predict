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
from functools import lru_cache

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

# Crop metadata derived from actual training dataset ranges
# N/P/K ranges, temperature, humidity, rainfall, pH from Crop_recommendation dataset
CROP_META: dict[str, dict[str, str]] = {
    # Crops present in the training dataset (22 classes)
    "rice":        {"emoji": "🌾", "water": "Very High", "yield": "4–6 t/ha",   "profit": "Medium",    "n_range": "60–99",   "p_range": "35–60",  "k_range": "35–45",  "rain": "~236 mm", "ph": "6.4"},
    "maize":       {"emoji": "🌽", "water": "Medium",    "yield": "3–6 t/ha",   "profit": "High",      "n_range": "60–100",  "p_range": "35–60",  "k_range": "15–25",  "rain": "~85 mm",  "ph": "6.2"},
    "jute":        {"emoji": "🌿", "water": "High",      "yield": "2–3 t/ha",   "profit": "Low",       "n_range": "60–100",  "p_range": "35–60",  "k_range": "35–45",  "rain": "~175 mm", "ph": "6.7"},
    "cotton":      {"emoji": "🌿", "water": "Medium",    "yield": "2–4 t/ha",   "profit": "High",      "n_range": "100–140", "p_range": "35–60",  "k_range": "15–25",  "rain": "~80 mm",  "ph": "6.9"},
    "coconut":     {"emoji": "🥥", "water": "High",      "yield": "5–8 t/ha",   "profit": "Medium",    "n_range": "0–40",    "p_range": "5–30",   "k_range": "25–35",  "rain": "~176 mm", "ph": "6.0"},
    "papaya":      {"emoji": "🍈", "water": "High",      "yield": "30–40 t/ha", "profit": "Medium",    "n_range": "31–70",   "p_range": "46–70",  "k_range": "45–55",  "rain": "~143 mm", "ph": "6.7"},
    "orange":      {"emoji": "🍊", "water": "Medium",    "yield": "15–25 t/ha", "profit": "High",      "n_range": "0–40",    "p_range": "5–30",   "k_range": "5–15",   "rain": "~111 mm", "ph": "7.0"},
    "apple":       {"emoji": "🍎", "water": "Medium",    "yield": "15–25 t/ha", "profit": "High",      "n_range": "0–40",    "p_range": "120–145","k_range": "195–205","rain": "~113 mm", "ph": "5.9"},
    "muskmelon":   {"emoji": "🍈", "water": "Low",       "yield": "10–20 t/ha", "profit": "Medium",    "n_range": "80–120",  "p_range": "5–30",   "k_range": "45–55",  "rain": "~25 mm",  "ph": "6.4"},
    "watermelon":  {"emoji": "🍉", "water": "Medium",    "yield": "20–30 t/ha", "profit": "Medium",    "n_range": "80–120",  "p_range": "5–30",   "k_range": "45–55",  "rain": "~51 mm",  "ph": "6.5"},
    "grapes":      {"emoji": "🍇", "water": "Medium",    "yield": "10–20 t/ha", "profit": "Very High", "n_range": "0–40",    "p_range": "120–145","k_range": "195–205","rain": "~70 mm",  "ph": "6.0"},
    "mango":       {"emoji": "🥭", "water": "Low",       "yield": "8–12 t/ha",  "profit": "High",      "n_range": "0–40",    "p_range": "15–40",  "k_range": "25–35",  "rain": "~95 mm",  "ph": "5.8"},
    "banana":      {"emoji": "🍌", "water": "High",      "yield": "20–30 t/ha", "profit": "Medium",    "n_range": "80–120",  "p_range": "70–95",  "k_range": "45–55",  "rain": "~105 mm", "ph": "6.0"},
    "pomegranate": {"emoji": "🍎", "water": "Low",       "yield": "8–12 t/ha",  "profit": "Very High", "n_range": "0–40",    "p_range": "5–30",   "k_range": "35–45",  "rain": "~108 mm", "ph": "6.4"},
    "lentil":      {"emoji": "🫘", "water": "Low",       "yield": "1–2 t/ha",   "profit": "Medium",    "n_range": "0–40",    "p_range": "55–80",  "k_range": "15–25",  "rain": "~46 mm",  "ph": "6.9"},
    "blackgram":   {"emoji": "🫘", "water": "Low",       "yield": "0.8–1.5 t/ha","profit": "Low",      "n_range": "20–60",   "p_range": "55–80",  "k_range": "15–25",  "rain": "~68 mm",  "ph": "7.1"},
    "mungbean":    {"emoji": "🫘", "water": "Low",       "yield": "1–2 t/ha",   "profit": "Low",       "n_range": "0–40",    "p_range": "35–60",  "k_range": "15–25",  "rain": "~48 mm",  "ph": "6.7"},
    "mothbeans":   {"emoji": "🫘", "water": "Low",       "yield": "0.5–1 t/ha", "profit": "Low",       "n_range": "0–40",    "p_range": "35–60",  "k_range": "15–25",  "rain": "~51 mm",  "ph": "6.8"},
    "pigeonpeas":  {"emoji": "🫘", "water": "Low",       "yield": "1–2 t/ha",   "profit": "Low",       "n_range": "0–40",    "p_range": "55–80",  "k_range": "15–25",  "rain": "~150 mm", "ph": "5.8"},
    "kidneybeans": {"emoji": "🫘", "water": "Medium",    "yield": "1–2 t/ha",   "profit": "Medium",    "n_range": "0–40",    "p_range": "55–80",  "k_range": "15–25",  "rain": "~106 mm", "ph": "5.8"},
    "chickpea":    {"emoji": "🫘", "water": "Low",       "yield": "1–2 t/ha",   "profit": "Medium",    "n_range": "20–60",   "p_range": "55–80",  "k_range": "75–85",  "rain": "~80 mm",  "ph": "7.3"},
    "coffee":      {"emoji": "☕", "water": "Medium",    "yield": "0.5–1 t/ha", "profit": "Very High", "n_range": "80–120",  "p_range": "15–40",  "k_range": "25–35",  "rain": "~158 mm", "ph": "6.8"},
}
_DEFAULT_META: dict[str, str] = {"emoji": "🌿", "water": "Medium", "yield": "Varies", "profit": "Medium"}


def crop_meta(name: str) -> dict[str, str]:
    return CROP_META.get(name.lower().strip(), _DEFAULT_META)


def crop_emoji(name: str) -> str:
    return crop_meta(name)["emoji"]


# ── Session state defaults ─────────────────────────────────────────────────────

# ── Dataset reference values (from Crop_recommendation.csv, 2200 rows) ───────
# Crop typical N / P / K / ph values from training data:
#   rice:      N=80,  P=48, K=40, ph=6.43, rain=236  ← good generic default
#   muskmelon: N=100, P=18, K=50, ph=6.36, rain=25   ← wins when rain≈0
#   maize:     N=78,  P=48, K=20, ph=6.25, rain=85
#   cotton:    N=118, P=46, K=20, ph=6.91, rain=80
# NOTE: Rain comes from live weather API — cannot be set here.
# Defaults below are dataset-representative to avoid biased initial output.

DEFAULTS: dict[str, Any] = {
    "lat":          None,
    "lon":          None,
    "n":            80.0,
    "p":            48.0,
    "k":            40.0,
    "ph":           6.5,
    "temperature":  25.0,
    "humidity":     70.0,
    "rainfall":     100.0,
    "top_k":        5,
    "last_result":  None,
    "last_weather": None,
    "history":      [],
    "request_geo":  False,
    "api_error":    None,
}


def init_session(st_module: Any) -> None:
    """Call once at app startup.  st_module is the imported streamlit module."""
    for k, v in DEFAULTS.items():
        if k not in st_module.session_state:
            st_module.session_state[k] = v


# ── API call ──────────────────────────────────────────────────────────────────

# ── Local model inference ────────────────────────────────────────────────────
# Models are loaded once at import time and cached.
# This eliminates all backend/API/deployment issues permanently.

import os as _os
from pathlib import Path as _Path
import numpy as _np

_ARTIFACTS_DIR = _Path(__file__).parent / "model_artifacts"


@lru_cache(maxsize=1)
def _load_models() -> tuple:
    """Load and cache RF + XGB models + preprocessor + labels."""
    try:
        import joblib as _joblib
        import json as _json

        labels = _json.loads((_ARTIFACTS_DIR / "labels.json").read_text())
        pre    = _joblib.load(_ARTIFACTS_DIR / "preprocessor.joblib")
        xgb    = _joblib.load(_ARTIFACTS_DIR / "xgboost.joblib")
        return labels, pre, xgb
    except Exception as exc:
        raise RuntimeError(f"Failed to load models: {exc}") from exc


def call_recommendations(
    lat: float, lon: float,
    n: float, p: float, k: float, ph: float,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Run inference LOCALLY using bundled model artifacts.
    No backend server needed — model runs directly in Streamlit.

    All 7 features are user-provided, matching the training data distribution
    exactly. Returns the same response format as the old REST API.
    """
    import warnings
    warnings.filterwarnings("ignore")

    try:
        labels, pre, xgb_model = _load_models()
    except RuntimeError as exc:
        raise NetworkError(str(exc)) from exc

    try:
        x   = _np.array([[n, p, k, temperature_c, humidity_pct, ph, rainfall_mm]],
                         dtype=_np.float32)
        xt  = pre.transform(x)
        ens   = xgb_model.predict_proba(xt)[0]

        k_safe = min(max(1, top_k), len(labels))
        top_idx = _np.argsort(-ens)[:k_safe].tolist()

        return {
            "weather": {
                "temperature_c":          temperature_c,
                "relative_humidity_pct":  humidity_pct,
                "rainfall_mm":            rainfall_mm,
            },
            "recommendations": [
                {"crop": labels[i], "probability": float(ens[i])}
                for i in top_idx
            ],
        }
    except Exception as exc:
        raise NetworkError(f"Local inference failed: {exc}") from exc


def check_api_health() -> bool:
    """Returns True if local model artifacts are loaded and ready."""
    try:
        _load_models()
        return True
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
    Based on actual training dataset ranges:
      N: 0–140 (dataset max), typical productive range 20–120
      P: 5–145 (dataset max), typical productive range 15–80
      K: 5–205 (dataset max), typical productive range 15–85
      pH: 3.5–9.9 (dataset), ideal 5.5–7.5
    Score reflects how well values fall within commonly cultivated ranges.
    """
    def _band(v: float, lo: float, hi: float, ok: int, near: int, far: int) -> int:
        if lo <= v <= hi:
            return ok
        half = (hi - lo) * 0.5
        if lo - half <= v <= hi + half:
            return near
        return far

    return min(100,
        _band(n,  20, 120, 30, 18, 5) +
        _band(p,  15,  80, 25, 14, 4) +
        _band(k,  15,  85, 25, 14, 4) +
        _band(ph, 5.5, 7.5, 20, 12, 3)
    )


def soil_tips(n: float, p: float, k: float, ph: float) -> list[tuple[str, str]]:
    """
    Returns list of (message, level) based on actual dataset crop ranges.
    Dataset N: 0–140, P: 5–145, K: 5–205, pH: 3.5–9.9
    """
    tips: list[tuple[str, str]] = []

    # Nitrogen — dataset range 0–140
    if n < 10:
        tips.append(("⚠️ Nitrogen very low (<10) — only suits low-N crops like coconut, orange. Apply urea for most crops.", "danger"))
    elif n < 20:
        tips.append(("💡 Nitrogen low (10–20) — suitable for pulses. Add compost or urea for cereals.", "warn"))
    elif n <= 120:
        tips.append(("✅ Nitrogen is in a productive range for most dataset crops.", "ok"))
    else:
        tips.append(("⚠️ Nitrogen very high (>120) — only cotton can use this level. Risk of leaf burn.", "warn"))

    # Phosphorus — dataset range 5–145
    if p < 5:
        tips.append(("⚠️ Phosphorus critically low — apply SSP or DAP immediately.", "danger"))
    elif p < 15:
        tips.append(("💡 Phosphorus low — suitable for muskmelon/watermelon. Add bone meal for other crops.", "warn"))
    elif p <= 80:
        tips.append(("✅ Phosphorus is in a productive range.", "ok"))
    elif p <= 145:
        tips.append(("💡 High phosphorus (>80) — ideal for apple and grapes only.", "info"))
    else:
        tips.append(("⚠️ Phosphorus exceeds dataset maximum — may inhibit zinc/iron uptake.", "danger"))

    # Potassium — dataset range 5–205
    if k < 5:
        tips.append(("⚠️ Potassium critically low — apply MOP or wood ash.", "danger"))
    elif k < 15:
        tips.append(("💡 Potassium low — suitable for orange only. Add potash for other crops.", "warn"))
    elif k <= 85:
        tips.append(("✅ Potassium is in a productive range for most crops.", "ok"))
    elif k <= 205:
        tips.append(("💡 Very high potassium (>85) — only apple/grapes grow in this range.", "info"))
    else:
        tips.append(("⚠️ Potassium exceeds dataset maximum.", "danger"))

    # pH — dataset range 3.5–9.9, most crops prefer 5.5–7.5
    if ph < 5.0:
        tips.append(("⚠️ Very acidic soil (pH<5) — apply agricultural lime to raise pH.", "danger"))
    elif ph < 5.5:
        tips.append(("💡 Mildly acidic — suitable for apple/banana/coffee. Add lime for neutral crops.", "warn"))
    elif ph <= 7.5:
        tips.append(("✅ pH is in the ideal range (5.5–7.5) for most dataset crops.", "ok"))
    elif ph <= 8.0:
        tips.append(("💡 Slightly alkaline — chickpea tolerates this. Watch micronutrient availability.", "warn"))
    else:
        tips.append(("⚠️ Highly alkaline (pH>8) — very few crops tolerate this. Apply elemental sulphur.", "danger"))

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