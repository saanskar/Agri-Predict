"""
Browser Geolocation Component  (ported from V1 ui/components/geolocation.py)
=============================================================================
Provides a Streamlit custom component that prompts the browser for GPS
lat/lon using the native Geolocation API.

Usage:
    from components.geolocation import get_browser_location

    result = get_browser_location(timeout_ms=10_000, key="geo_1")
    # result is:
    #   None          — still waiting for browser
    #   {"lat": ..., "lon": ..., "accuracy_m": ...} on success
    #   {"error": ..., "code": ...}                 on failure
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).resolve().parent / "geolocation_frontend"

_component: Callable[..., Any] | None
_declare_error: str | None = None

try:
    _component = components.declare_component(
        "agripredict_geolocation",
        path=str(_FRONTEND_DIR),
    )
except RuntimeError as exc:
    _component = None
    _declare_error = str(exc)


def get_browser_location(*, timeout_ms: int = 10_000, key: str) -> dict[str, Any] | None:
    """
    Invoke the browser Geolocation API via the custom Streamlit component.

    Returns:
        None                  — awaiting browser permission/response
        dict with lat/lon     — success: {"lat": float, "lon": float, "accuracy_m": float}
        dict with error       — failure: {"error": str, "code": int | None}
    """
    if _component is None:
        return {"error": _declare_error or "Geolocation component could not be initialised."}

    value = _component(timeout_ms=timeout_ms, key=key)
    return cast(dict[str, Any] | None, value)
