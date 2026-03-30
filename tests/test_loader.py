"""
@design-guard
role: Unit tests for training dataset loader behavior.
layer: service
non_goals:
- Validate agronomic realism of data.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Loader must return expected columns and non-empty data.
authority:
  decides: [loader_test_contract]
  delegates: []
extension_policy:
- Update tests alongside schema changes.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Unit tests only; deterministic and fast.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from ml.data.loader import EXPECTED_COLUMNS, load_training_dataframe


def test_load_training_dataframe_default_is_non_empty_and_schema_correct() -> None:
    df = load_training_dataframe()
    assert list(df.columns) == list(EXPECTED_COLUMNS)
    assert len(df) > 0
