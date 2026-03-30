"""
@design-guard
role: Unit test Open-Meteo weather provider parsing.
layer: service
non_goals:
- Live network testing.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Provider must map vendor payload to WeatherSnapshot units correctly.
authority:
  decides: [weather_provider_test_contract]
  delegates: []
extension_policy:
- Update tests if Open-Meteo payload mapping changes.
failure_contract:
- Fail fast with clear assertions.
testing_contract:
- Async unit tests using httpx MockTransport.
references:
- docs/ADRs/0002-weather-provider.md
"""

from __future__ import annotations

import json

import httpx
import pytest

from backend.app.services.weather.open_meteo import OpenMeteoWeatherProvider
from backend.app.services.weather.provider import WeatherQuery


@pytest.mark.anyio
async def test_open_meteo_parses_current_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = {"current": {"temperature_2m": 25.5, "relative_humidity_2m": 60, "rain": 2.25}}
        return httpx.Response(200, content=json.dumps(payload).encode("utf-8"))

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoWeatherProvider(client=client)
        snap = await provider.get_weather(WeatherQuery(lat=10.0, lon=20.0))

    assert snap.temperature_c == 25.5
    assert snap.relative_humidity_pct == 60.0
    assert snap.rainfall_mm == 2.25
