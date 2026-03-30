"""
@design-guard
role: Train and serve a RandomForest classifier for crop recommendation.
layer: service
non_goals:
- Feature scaling (handled by shared preprocessor).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [train_random_forest]
invariants:
- Random seed is explicit for determinism.
authority:
  decides: [rf_hyperparameters_default]
  delegates: []
extension_policy:
- Tune hyperparameters behind a config object, not scattered kwargs.
failure_contract:
- Raise on fit failures.
testing_contract:
- Unit tests validate predict_proba shape and class ordering consistency.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestClassifier


def train_random_forest(
    x_train: NDArray[np.float32],
    y_train: NDArray[np.int64],
    *,
    seed: int,
    n_estimators: int = 250,
) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model
