"""
@design-guard
role: FastAPI application entrypoint and dependency wiring.
layer: facade
non_goals:
- ML training.
- Direct HTTP calls to weather providers (delegated).
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [fastapi_app]
invariants:
- Routes are registered via the api layer; keep wiring explicit.
authority:
  decides: [app_configuration, dependency_wiring]
  delegates: [request_handling_to_routes, domain_logic_to_services]
extension_policy:
- Add new routes via api router modules, not inline.
failure_contract:
- Fail fast on misconfiguration at startup.
testing_contract:
- Covered by API integration tests via FastAPI TestClient.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from backend.app.api.routes import router as api_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(title="AgriPredict API", lifespan=_lifespan)
app.include_router(api_router)
