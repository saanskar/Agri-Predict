"""
@design-guard
role: Load the crop recommendation dataset for training.
layer: service
non_goals:
- Download datasets from external sources.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [load_training_dataframe]
invariants:
- Output schema matches expected feature columns + label.
authority:
  decides: [dataset_loading_policy]
  delegates: [synthetic_generation_to_generator]
extension_policy:
- Add new loaders as separate functions with explicit schemas.
failure_contract:
- Raise on missing/invalid schema.
testing_contract:
- Unit tests validate required columns and types.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.data.synthetic_dataset import SyntheticDatasetConfig, generate_synthetic_dataset

EXPECTED_COLUMNS: tuple[str, ...] = (
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "label",
)


def load_training_dataframe(data_path: Path | None = None) -> pd.DataFrame:
    if data_path is None:
        df = generate_synthetic_dataset(SyntheticDatasetConfig(samples_per_crop=80, seed=1337))
    else:
        df = pd.read_csv(data_path)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    return df.loc[:, list(EXPECTED_COLUMNS)].copy()
