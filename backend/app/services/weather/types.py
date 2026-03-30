"""
@design-guard
role: Define internal weather value objects used by inference feature building.
layer: domain
non_goals:
- Persisting weather data.
boundaries:
  depends_on_layers: [domain]
  exposes: [WeatherSnapshot]
invariants:
- All numeric values use explicit units (documented in field names).
authority:
  decides: [weather_value_object_shape]
  delegates: []
extension_policy:
- Extend by adding fields with clear units; avoid ambiguous names.
failure_contract:
- No runtime behavior.
testing_contract:
- Unit tests validate parsing/construction in provider implementations.
references:
- docs/ADRs/0002-weather-provider.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherSnapshot:
    temperature_c: float
    relative_humidity_pct: float
    rainfall_mm: float
