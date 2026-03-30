"""
@design-guard
role: Unit tests for synthetic dataset determinism and schema.
layer: service
non_goals:
- Validate agronomic correctness of the synthetic data.
boundaries:
  depends_on_layers: [service]
  exposes: [pytest_tests]
invariants:
- Generated dataset must be deterministic for a fixed seed.
authority:
  decides: [synthetic_dataset_test_contract]
  delegates: []
extension_policy:
- Update tests if schema changes.
failure_contract:
- Fail with clear assertions.
testing_contract:
- Unit tests only; fast and deterministic.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from ml.data.synthetic_dataset import SyntheticDatasetConfig, generate_synthetic_dataset


def test_synthetic_dataset_is_deterministic() -> None:
    df1 = generate_synthetic_dataset(SyntheticDatasetConfig(samples_per_crop=3, seed=123))
    df2 = generate_synthetic_dataset(SyntheticDatasetConfig(samples_per_crop=3, seed=123))
    assert df1.equals(df2)


def test_synthetic_dataset_has_expected_columns() -> None:
    df = generate_synthetic_dataset(SyntheticDatasetConfig(samples_per_crop=2, seed=1))
    assert set(df.columns) == {"N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"}
