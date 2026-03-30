"""
@design-guard
role: Unit tests for artifact-backed ensemble inference runtime.
layer: service
non_goals:
- Validate model accuracy.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Given valid artifacts, recommend returns top-k sorted by probability.
authority:
  decides: [runtime_inference_test_contract]
  delegates: []
extension_policy:
- Extend tests when adding new model legs or artifact formats.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Use temporary artifacts; do not depend on network.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pytest
import torch
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.schemas import SoilSample
from backend.app.services.inference.runtime import ArtifactEnsembleInferenceService
from backend.app.services.inference.service import InferenceUnavailableError
from backend.app.services.weather.types import WeatherSnapshot
from ml.features import FEATURE_COLUMNS
from ml.models.nn_model import Net
from ml.models.rf_model import train_random_forest
from ml.models.xgb_model import train_xgboost
from ml.registry import ArtifactPaths


def _write_artifacts(root: Path) -> None:
    labels = ["a", "b", "c"]
    x = np.array(
        [
            [10, 10, 10, 20, 50, 6.5, 80],
            [90, 40, 20, 30, 70, 5.8, 120],
            [40, 80, 70, 25, 60, 7.2, 40],
            [15, 20, 90, 18, 55, 6.0, 200],
            [60, 25, 35, 22, 45, 6.8, 70],
        ],
        dtype=np.float32,
    )
    y = np.array([0, 1, 2, 0, 1], dtype=np.int64)

    pre = Pipeline([("scaler", StandardScaler())])
    x_t = pre.fit_transform(x).astype(np.float32, copy=False)

    rf = train_random_forest(x_t, y, seed=1, n_estimators=20)
    xgb = train_xgboost(x_t, y, seed=1, n_estimators=25)

    torch.manual_seed(1)
    net = Net(input_dim=len(FEATURE_COLUMNS), output_dim=len(labels))

    paths = ArtifactPaths(root=root)
    paths.root.mkdir(parents=True, exist_ok=True)
    joblib.dump(pre, paths.preprocessor_path)
    joblib.dump(rf, paths.rf_model_path)
    joblib.dump(xgb, paths.xgb_model_path)
    torch.save(net.state_dict(), paths.nn_model_path)
    paths.labels_path.write_text(json.dumps(labels), encoding="utf-8")


@pytest.mark.anyio
async def test_recommend_returns_top_k(tmp_path: Path) -> None:
    artifacts_root = tmp_path / "artifacts"
    _write_artifacts(artifacts_root)

    svc = ArtifactEnsembleInferenceService(artifacts_dir=str(artifacts_root))
    recs = await svc.recommend(
        soil=SoilSample(n=10, p=10, k=10, ph=6.5),
        weather=WeatherSnapshot(temperature_c=25.0, relative_humidity_pct=60.0, rainfall_mm=2.0),
        top_k=2,
    )

    assert len(recs) == 2
    assert all(0.0 <= r.probability <= 1.0 for r in recs)
    assert recs[0].probability >= recs[1].probability


@pytest.mark.anyio
async def test_missing_artifacts_directory_raises(tmp_path: Path) -> None:
    svc = ArtifactEnsembleInferenceService(artifacts_dir=str(tmp_path / "missing"))
    with pytest.raises(InferenceUnavailableError):
        await svc.recommend(
            soil=SoilSample(n=1, p=1, k=1, ph=7.0),
            weather=WeatherSnapshot(
                temperature_c=20.0, relative_humidity_pct=50.0, rainfall_mm=0.0
            ),
            top_k=1,
        )
