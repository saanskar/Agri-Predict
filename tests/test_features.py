"""
@design-guard
role: Unit tests for feature schema and matrix building.
layer: service
non_goals:
- Full model training tests.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Feature column order must remain stable.
authority:
  decides: [test_coverage_for_features]
  delegates: []
extension_policy:
- Update tests alongside any feature schema changes.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Unit tests only; deterministic and fast.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

import numpy as np

from ml.features import FEATURE_COLUMNS, as_numpy_matrix


def test_feature_columns_are_stable() -> None:
    assert FEATURE_COLUMNS == ("N", "P", "K", "temperature", "humidity", "ph", "rainfall")


def test_as_numpy_matrix_builds_expected_shape_and_order() -> None:
    rows = [
        {
            "N": 1.0,
            "P": 2.0,
            "K": 3.0,
            "temperature": 4.0,
            "humidity": 5.0,
            "ph": 6.0,
            "rainfall": 7.0,
        },
        {
            "N": 10.0,
            "P": 20.0,
            "K": 30.0,
            "temperature": 40.0,
            "humidity": 50.0,
            "ph": 60.0,
            "rainfall": 70.0,
        },
    ]
    mat = as_numpy_matrix(rows)
    assert mat.shape == (2, 7)
    assert mat.dtype == np.float32
    assert np.allclose(mat[0], np.array([1, 2, 3, 4, 5, 6, 7], dtype=np.float32))
