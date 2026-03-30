"""
@design-guard
role: Unit tests for model wrapper contracts (predict_proba shapes).
layer: service
non_goals:
- Validate accuracy metrics.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- All wrappers must produce a (n_samples, n_classes) probability matrix.
authority:
  decides: [wrapper_contract_tests]
  delegates: []
extension_policy:
- Keep datasets tiny for speed; test only contract-level behavior.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Unit tests only; deterministic and fast.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import numpy as np

from ml.models.nn_model import train_neural_net
from ml.models.rf_model import train_random_forest
from ml.models.xgb_model import train_xgboost


def test_random_forest_predict_proba_shape() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=(40, 7)).astype(np.float32)
    y = rng.integers(low=0, high=3, size=(40,), dtype=np.int64)
    model = train_random_forest(x, y, seed=123, n_estimators=30)
    probs = model.predict_proba(x)
    probs_arr = np.asarray(probs)
    assert probs_arr.shape == (40, 3)


def test_xgboost_predict_proba_shape() -> None:
    rng = np.random.default_rng(2)
    x = rng.normal(size=(50, 7)).astype(np.float32)
    y = rng.integers(low=0, high=4, size=(50,), dtype=np.int64)
    model = train_xgboost(x, y, seed=123, n_estimators=25)
    probs = model.predict_proba(x)
    probs_arr = np.asarray(probs)
    assert probs_arr.shape == (50, 4)


def test_neural_net_predict_proba_shape() -> None:
    rng = np.random.default_rng(3)
    x = rng.normal(size=(60, 7)).astype(np.float32)
    y = rng.integers(low=0, high=5, size=(60,), dtype=np.int64)
    clf = train_neural_net(x, y, seed=123, epochs=3)
    probs = clf.predict_proba(x)
    assert probs.shape == (60, 5)
