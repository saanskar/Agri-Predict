"""
@design-guard
role: Define API request/response schemas and shared value objects.
layer: domain
non_goals:
- Business logic or I/O.
boundaries:
  depends_on_layers: [domain]
  exposes: [pydantic_models]
invariants:
- Schemas are stable contracts; avoid leaking internal implementation details.
authority:
  decides: [request_response_shape]
  delegates: []
extension_policy:
- Prefer additive changes; maintain backward compatibility when possible.
failure_contract:
- Validation errors are surfaced by pydantic/FastAPI.
testing_contract:
- Unit tests should validate schema constraints for critical fields.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class SoilSample(BaseModel):
    n: float = Field(ge=0)
    p: float = Field(ge=0)
    k: float = Field(ge=0)
    ph: float = Field(ge=0, le=14)


class RecommendationRequest(BaseModel):
    location: Location
    soil: SoilSample
    top_k: int = Field(default=5, ge=1, le=10)


class WeatherUsed(BaseModel):
    temperature_c: float
    relative_humidity_pct: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)


class RecommendationItem(BaseModel):
    crop: str = Field(min_length=1)
    probability: float = Field(ge=0, le=1)


class RecommendationsResponse(BaseModel):
    weather: WeatherUsed
    recommendations: list[RecommendationItem]
