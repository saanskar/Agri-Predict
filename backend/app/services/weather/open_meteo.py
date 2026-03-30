"""
@design-guard
role: Implement WeatherProvider using Open-Meteo.
layer: service
non_goals:
- Cache strategy or persistence.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [OpenMeteoWeatherProvider]
invariants:
- Map vendor payload to WeatherSnapshot with explicit units.
authority:
  decides: [vendor_api_mapping]
  delegates: [http_to_httpx]
extension_policy:
- Keep HTTP and parsing logic cohesive; do not leak vendor schema outward.
failure_contract:
- Raise WeatherUnavailable on network/parse failures.
testing_contract:
- Unit tests should cover payload parsing and error handling.
references:
- docs/ADRs/0002-weather-provider.md
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from backend.app.services.weather.provider import (
    WeatherProvider,
    WeatherQuery,
    WeatherUnavailableError,
)
from backend.app.services.weather.types import WeatherSnapshot


@dataclass(frozen=True)
class OpenMeteoWeatherProvider(WeatherProvider):
    client: httpx.AsyncClient

    async def get_weather(self, query: WeatherQuery) -> WeatherSnapshot:
        try:
            resp = await self.client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": query.lat,
                    "longitude": query.lon,
                    "current": ["temperature_2m", "relative_humidity_2m", "rain"],
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            payload = resp.json()
            current = payload["current"]
            return WeatherSnapshot(
                temperature_c=float(current["temperature_2m"]),
                relative_humidity_pct=float(current["relative_humidity_2m"]),
                rainfall_mm=float(current["rain"]),
            )
        except Exception as exc:
            raise WeatherUnavailableError("Weather provider failed") from exc
