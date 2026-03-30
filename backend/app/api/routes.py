"""
@design-guard
role: Expose HTTP endpoints and delegate to services for execution.
layer: facade
non_goals:
- Implement recommendation logic; only request/response mapping.
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [api_router]
invariants:
- All inputs/outputs validated via pydantic schemas.
authority:
  decides: [http_contract_mapping]
  delegates: [recommendation_to_inference_service, weather_to_weather_service]
extension_policy:
- Add endpoints by composing smaller service interfaces.
failure_contract:
- Surface validation errors via FastAPI; translate service errors to HTTP errors.
testing_contract:
- Integration tests must cover success + validation failures.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_inference_service, get_weather_provider
from backend.app.schemas import (
    RecommendationItem,
    RecommendationRequest,
    RecommendationsResponse,
    WeatherUsed,
)
from backend.app.services.inference.service import InferenceService, InferenceUnavailableError
from backend.app.services.weather.provider import (
    WeatherProvider,
    WeatherQuery,
    WeatherUnavailableError,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/recommendations", response_model=RecommendationsResponse)
async def recommendations(
    payload: RecommendationRequest,
    weather_provider: WeatherProvider = Depends(get_weather_provider),
    inference_service: InferenceService = Depends(get_inference_service),
) -> RecommendationsResponse:
    try:
        weather = await weather_provider.get_weather(
            WeatherQuery(lat=payload.location.lat, lon=payload.location.lon)
        )
        recs = await inference_service.recommend(
            soil=payload.soil, weather=weather, top_k=payload.top_k
        )
        return RecommendationsResponse(
            weather=WeatherUsed(
                temperature_c=weather.temperature_c,
                relative_humidity_pct=weather.relative_humidity_pct,
                rainfall_mm=weather.rainfall_mm,
            ),
            recommendations=[
                RecommendationItem(crop=r.crop, probability=r.probability) for r in recs
            ],
        )
    except WeatherUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except InferenceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
