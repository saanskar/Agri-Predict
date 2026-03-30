"""
@design-guard
role: Define the WeatherProvider interface for dependency injection.
layer: service
non_goals:
- Bind to a specific vendor API.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [WeatherProvider]
invariants:
- Provider implementations must return fully-populated WeatherSnapshot.
authority:
  decides: [provider_interface_contract]
  delegates: []
extension_policy:
- Add provider-specific options via separate config objects, not extra params.
failure_contract:
- Raise WeatherUnavailable on failure; do not return None/partials.
testing_contract:
- Unit tests should validate error mapping and success parsing.
references:
- docs/ADRs/0002-weather-provider.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.app.services.weather.types import WeatherSnapshot


class WeatherUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class WeatherQuery:
    lat: float
    lon: float


class WeatherProvider(Protocol):
    async def get_weather(self, query: WeatherQuery) -> WeatherSnapshot: ...
