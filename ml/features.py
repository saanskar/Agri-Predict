"""
@design-guard
role: Define the feature pipeline used by training and inference.
layer: service
non_goals:
- Perform model training directly.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [FeatureVector, build_features_contract]
invariants:
- Feature schema is explicit and stable across training/inference.
authority:
  decides: [feature_schema_and_order]
  delegates: []
extension_policy:
- Add features only with a corresponding dataset column and tests.
failure_contract:
- Raise ValueError on invalid inputs; do not coerce silently.
testing_contract:
- Unit tests must validate deterministic ordering and scaling.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class FeatureVector:
    values: tuple[float, ...]


FEATURE_COLUMNS: tuple[str, ...] = (
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
)


def as_numpy_matrix(rows: list[dict[str, float]]) -> NDArray[np.float32]:
    matrix = np.array([[row[c] for c in FEATURE_COLUMNS] for row in rows], dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] != len(FEATURE_COLUMNS):
        raise ValueError("Invalid feature matrix shape.")
    return matrix
