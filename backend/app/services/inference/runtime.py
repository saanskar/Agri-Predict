"""
@design-guard
role: Load trained artifacts and compute ensemble crop recommendations.
layer: service
non_goals:
- Train models (ml package responsibility).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [ArtifactEnsembleInferenceService]
invariants:
- Probability vectors are aligned to the same label ordering.
authority:
  decides: [ensemble_strategy_soft_voting, artifact_loading_policy]
  delegates: [weather_features_to_weather_service]
extension_policy:
- Add new model legs via explicit interface + probability alignment tests.
failure_contract:
- Raise InferenceUnavailable on missing/corrupt artifacts.
testing_contract:
- Unit tests must validate probability alignment and ranking determinism.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from backend.app.schemas import SoilSample
from backend.app.services.inference.service import (
    InferenceService,
    InferenceUnavailableError,
)
from backend.app.services.inference.types import CropRecommendation
from backend.app.services.weather.types import WeatherSnapshot
from ml.features import FEATURE_COLUMNS
from ml.models.nn_model import Net, NeuralNetClassifier
from ml.registry import ArtifactPaths, load_joblib, load_labels


def _build_feature_row(*, soil: SoilSample, weather: WeatherSnapshot) -> NDArray[np.float32]:
    row = {
        "N": float(soil.n),
        "P": float(soil.p),
        "K": float(soil.k),
        "temperature": float(weather.temperature_c),
        "humidity": float(weather.relative_humidity_pct),
        "ph": float(soil.ph),
        "rainfall": float(weather.rainfall_mm),
    }
    return np.array([[row[c] for c in FEATURE_COLUMNS]], dtype=np.float32)


def _safe_top_k(k: int, total: int) -> int:
    if k <= 0:
        return 1
    return min(k, total)


@dataclass(frozen=True)
class _LoadedArtifacts:
    labels: list[str]
    preprocessor: object
    rf: object
    xgb: object
    nn: NeuralNetClassifier


@lru_cache(maxsize=1)
def _load_artifacts(artifacts_dir: str) -> _LoadedArtifacts:
    root = Path(artifacts_dir)
    paths = ArtifactPaths(root=root)
    if not root.exists():
        raise InferenceUnavailableError(f"Artifacts directory not found: {root}")

    try:
        labels = load_labels(paths)
        pre = load_joblib(paths.preprocessor_path)
        rf = load_joblib(paths.rf_model_path)
        xgb = load_joblib(paths.xgb_model_path)

        # Reconstruct NN architecture from label count.
        import torch

        net = Net(input_dim=len(FEATURE_COLUMNS), output_dim=len(labels))
        state = torch.load(paths.nn_model_path, map_location="cpu")
        net.load_state_dict(state)
        nn = NeuralNetClassifier(net=net)

        return _LoadedArtifacts(labels=labels, preprocessor=pre, rf=rf, xgb=xgb, nn=nn)
    except Exception as exc:
        raise InferenceUnavailableError("Failed to load inference artifacts") from exc


def _predict_proba(model: object, x: NDArray[np.float32]) -> NDArray[np.float32]:
    predict_proba = getattr(model, "predict_proba", None)
    if predict_proba is None:
        raise InferenceUnavailableError("Model does not expose predict_proba")
    probs = predict_proba(x)
    probs_arr = np.asarray(probs, dtype=np.float32)
    if probs_arr.ndim != 2:
        raise InferenceUnavailableError("Invalid probability shape")
    return probs_arr


@dataclass(frozen=True)
class ArtifactEnsembleInferenceService(InferenceService):
    artifacts_dir: str

    async def recommend(
        self, *, soil: SoilSample, weather: WeatherSnapshot, top_k: int
    ) -> tuple[CropRecommendation, ...]:
        art = _load_artifacts(self.artifacts_dir)
        x = _build_feature_row(soil=soil, weather=weather)

        transform = getattr(art.preprocessor, "transform", None)
        if transform is None:
            raise InferenceUnavailableError("Preprocessor does not expose transform")
        x_t = np.asarray(transform(x), dtype=np.float32)

        rf_p = _predict_proba(art.rf, x_t)
        xgb_p = _predict_proba(art.xgb, x_t)
        nn_p = np.asarray(art.nn.predict_proba(x_t), dtype=np.float32)

        if rf_p.shape != xgb_p.shape or rf_p.shape != nn_p.shape:
            raise InferenceUnavailableError("Probability shapes do not align across models")

        ensemble = (rf_p + xgb_p + nn_p) / 3.0
        probs = ensemble[0]

        k = _safe_top_k(top_k, len(art.labels))
        top_idx = np.argsort(-probs)[:k].tolist()

        recs = tuple(
            CropRecommendation(crop=art.labels[i], probability=float(probs[i])) for i in top_idx
        )
        return recs
