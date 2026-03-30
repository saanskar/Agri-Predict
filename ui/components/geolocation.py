"""
@design-guard
role: Provide a browser geolocation Streamlit component to fetch lat/lon.
layer: ui
non_goals:
- Geocoding (city->lat/lon) or persistence.
- Backend requests; this is UI-only.
boundaries:
  depends_on_layers: [ui]
  exposes: [get_browser_location]
invariants:
- Returned values are JSON-serializable and may be None until resolved.
authority:
  decides: [component_contract_and_defaults]
  delegates: [location_fetch_to_browser]
extension_policy:
- Add optional parameters via kwargs passed to the component.
failure_contract:
- Return a dict containing an error message instead of raising.
testing_contract:
- Manual verification (requires browser permissions); keep python wrapper minimal.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import streamlit.components.v1 as components

frontend_dir = Path(__file__).resolve().parent / "geolocation_frontend"

_component: Callable[..., Any] | None
_declare_error: str | None = None
try:
    _component = components.declare_component(
        "agripredict_geolocation",
        path=str(frontend_dir),
    )
except RuntimeError as exc:
    _component = None
    _declare_error = str(exc)


def get_browser_location(*, timeout_ms: int = 10000, key: str) -> dict[str, Any] | None:
    """
    Returns:
      - None while awaiting browser permission/response.
      - dict with keys: {lat, lon, accuracy_m} on success.
      - dict with keys: {error, code?} on failure.
    """
    if _component is None:
        return {"error": _declare_error or "Geolocation component could not be initialized."}

    value = _component(timeout_ms=timeout_ms, key=key)
    return cast(dict[str, Any] | None, value)
