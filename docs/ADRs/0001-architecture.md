# ADR 0001: Layered architecture with API + UI + ML packages

## Context

AgriPredict needs a farmer-friendly UI, a robust backend API, and a maintainable hybrid ML stack (RF/XGB/NN) with live weather enrichment.

## Decision

Adopt a layered architecture with three top-level packages:

- `backend/`: FastAPI app providing prediction endpoints and weather enrichment.
- `ml/`: model training, feature pipeline, and artifact registry used by inference.
- `ui/`: Streamlit UI calling the backend API (no direct model access).

## Rationale

- Keeps responsibilities separated and supports SOLID boundaries.
- Supports dependency injection (interfaces for weather and inference services).
- Enables independent testing at each boundary.

## Consequences

- Inference artifacts are produced by `ml/` and loaded by `backend/` at runtime.
- UI remains thin and stable even as models evolve.

