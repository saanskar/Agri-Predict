"""
@design-guard
role: Train and serve an XGBoost classifier for crop recommendation.
layer: service
non_goals:
- Cross-validation or large-scale tuning.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [train_xgboost]
invariants:
- Training is deterministic given seed (as supported by the library).
authority:
  decides: [xgb_hyperparameters_default]
  delegates: []
extension_policy:
- Tune hyperparameters behind a config object.
failure_contract:
- Raise on fit failures.
testing_contract:
- Unit tests validate predict_proba shape and class ordering.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from xgboost import XGBClassifier


def train_xgboost(
    x_train: NDArray[np.float32],
    y_train: NDArray[np.int64],
    *,
    seed: int,
    n_estimators: int = 400,
) -> XGBClassifier:
    model = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=seed,
        n_jobs=0,
    )
    model.fit(x_train, y_train)
    return model
