"""
@design-guard
role: Centralize FastAPI dependency injection wiring for services.
layer: facade
non_goals:
- Implement business logic; only create/wire services.
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [dependency_providers]
invariants:
- Dependencies are explicit and easily stubbed in tests.
authority:
  decides: [singleton_vs_per_request_instances]
  delegates: [logic_to_services]
extension_policy:
- Add dependencies via new provider functions, not hidden globals.
failure_contract:
- Raise clear errors on missing app state/resources.
testing_contract:
- Integration tests can override dependencies for determinism.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import Request

from backend.app.services.inference.runtime import ArtifactEnsembleInferenceService
from backend.app.services.inference.service import InferenceService
from backend.app.services.weather.open_meteo import OpenMeteoWeatherProvider
from backend.app.services.weather.provider import WeatherProvider


def get_http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise RuntimeError("HTTP client not initialized in app state.")
    if not isinstance(client, httpx.AsyncClient):
        raise RuntimeError("Invalid http_client type in app state.")
    return client


def get_weather_provider(request: Request) -> WeatherProvider:
    return OpenMeteoWeatherProvider(client=get_http_client(request))


@lru_cache(maxsize=1)
def _artifact_dir() -> str:
    return os.environ.get("AGRIPREDICT_ARTIFACTS_DIR", "artifacts")


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    return ArtifactEnsembleInferenceService(artifacts_dir=_artifact_dir())
