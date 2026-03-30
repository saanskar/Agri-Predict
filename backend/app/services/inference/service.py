"""
@design-guard
role: Define the inference service interface to produce crop recommendations.
layer: service
non_goals:
- Implement concrete model execution (delegated to ml artifact wrappers).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [InferenceService, InferenceUnavailable]
invariants:
- Deterministic output given fixed artifacts and inputs.
authority:
  decides: [inference_service_contract]
  delegates: [model_execution_to_artifact_runtime]
extension_policy:
- Keep API stable; prefer adding optional strategy objects over params.
failure_contract:
- Raise InferenceUnavailable on any model/artifact failures.
testing_contract:
- Unit tests with stub artifacts; integration tests through API route.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from typing import Protocol

from backend.app.schemas import SoilSample
from backend.app.services.inference.types import CropRecommendation
from backend.app.services.weather.types import WeatherSnapshot


class InferenceUnavailableError(RuntimeError):
    pass


class InferenceService(Protocol):
    async def recommend(
        self, *, soil: SoilSample, weather: WeatherSnapshot, top_k: int
    ) -> tuple[CropRecommendation, ...]: ...
