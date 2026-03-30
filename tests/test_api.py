"""
@design-guard
role: Integration/system tests for FastAPI endpoints using dependency overrides.
layer: service
non_goals:
- Validate ML accuracy (covered separately).
boundaries:
  depends_on_layers: [service, facade, domain]
  exposes: [pytest_tests]
invariants:
- Tests must not perform live network calls.
authority:
  decides: [api_test_contract]
  delegates: []
extension_policy:
- Add tests for new endpoints and failure modes.
failure_contract:
- Fail fast with clear assertions.
testing_contract:
- System-level API tests via TestClient with DI stubs.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request
from fastapi.testclient import TestClient

from backend.app.dependencies import get_inference_service, get_weather_provider
from backend.app.main import app
from backend.app.schemas import SoilSample
from backend.app.services.inference.service import InferenceService
from backend.app.services.inference.types import CropRecommendation
from backend.app.services.weather.provider import WeatherProvider, WeatherQuery
from backend.app.services.weather.types import WeatherSnapshot


@dataclass(frozen=True)
class _StubWeatherProvider(WeatherProvider):
    async def get_weather(self, query: WeatherQuery) -> WeatherSnapshot:
        del query
        return WeatherSnapshot(temperature_c=24.0, relative_humidity_pct=55.0, rainfall_mm=1.0)


@dataclass(frozen=True)
class _StubInferenceService(InferenceService):
    async def recommend(
        self, *, soil: SoilSample, weather: WeatherSnapshot, top_k: int
    ) -> tuple[CropRecommendation, ...]:
        del soil, weather
        k = max(1, min(int(top_k), 3))
        base = (
            CropRecommendation(crop="rice", probability=0.7),
            CropRecommendation(crop="maize", probability=0.2),
            CropRecommendation(crop="coffee", probability=0.1),
        )
        return base[:k]


def test_health_ok() -> None:
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_recommendations_success_with_dependency_overrides() -> None:
    def _override_weather_provider(request: Request) -> WeatherProvider:
        del request
        return _StubWeatherProvider()

    app.dependency_overrides[get_weather_provider] = _override_weather_provider
    app.dependency_overrides[get_inference_service] = lambda: _StubInferenceService()

    with TestClient(app) as client:
        resp = client.post(
            "/recommendations",
            json={
                "location": {"lat": 10.0, "lon": 20.0},
                "soil": {"n": 10, "p": 10, "k": 10, "ph": 6.5},
                "top_k": 2,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["weather"]["temperature_c"] == 24.0
        assert len(body["recommendations"]) == 2
        assert body["recommendations"][0]["crop"] == "rice"

    app.dependency_overrides.clear()


def test_recommendations_validation_error() -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/recommendations",
            json={
                "location": {"lat": 999.0, "lon": 0.0},
                "soil": {"n": 1, "p": 1, "k": 1, "ph": 7},
            },
        )
        assert resp.status_code == 422
