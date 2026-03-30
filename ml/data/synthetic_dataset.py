"""
@design-guard
role: Generate a deterministic synthetic crop dataset for training/demo.
layer: service
non_goals:
- Claim real agronomic validity; this is a demo dataset.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [generate_synthetic_dataset]
invariants:
- Output is deterministic given seed.
authority:
  decides: [synthetic_distributions, label_set]
  delegates: []
extension_policy:
- Adjust distributions only alongside model/tests updates.
failure_contract:
- Raise on invalid parameters.
testing_contract:
- Unit tests validate schema/shape and determinism.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticDatasetConfig:
    samples_per_crop: int
    seed: int


_CROPS: tuple[str, ...] = (
    "rice",
    "maize",
    "chickpea",
    "kidneybeans",
    "pigeonpeas",
    "mungbean",
    "blackgram",
    "lentil",
    "pomegranate",
    "banana",
    "mango",
    "grapes",
    "watermelon",
    "muskmelon",
    "apple",
    "orange",
    "papaya",
    "coconut",
    "cotton",
    "jute",
    "coffee",
)


def crop_labels() -> tuple[str, ...]:
    return _CROPS


def generate_synthetic_dataset(config: SyntheticDatasetConfig) -> pd.DataFrame:
    if config.samples_per_crop <= 0:
        raise ValueError("samples_per_crop must be > 0")

    rng = np.random.default_rng(config.seed)

    rows: list[dict[str, float | str]] = []
    for idx, crop in enumerate(_CROPS):
        # Each crop gets different means but stays in plausible ranges.
        n_mu = 20 + (idx % 7) * 10
        p_mu = 15 + (idx % 5) * 8
        k_mu = 20 + (idx % 6) * 9
        temp_mu = 18 + (idx % 8) * 2.5
        hum_mu = 45 + (idx % 6) * 7
        ph_mu = 5.5 + (idx % 5) * 0.4
        rain_mu = 60 + (idx % 7) * 20

        for _ in range(config.samples_per_crop):
            rows.append(
                {
                    "N": float(rng.normal(n_mu, 8)),
                    "P": float(rng.normal(p_mu, 6)),
                    "K": float(rng.normal(k_mu, 7)),
                    "temperature": float(rng.normal(temp_mu, 3)),
                    "humidity": float(rng.normal(hum_mu, 10)),
                    "ph": float(rng.normal(ph_mu, 0.35)),
                    "rainfall": float(rng.normal(rain_mu, 25)),
                    "label": crop,
                }
            )

    df = pd.DataFrame(rows)
    # Clip to stable ranges and avoid negatives where non-sensical.
    df["N"] = df["N"].clip(lower=0)
    df["P"] = df["P"].clip(lower=0)
    df["K"] = df["K"].clip(lower=0)
    df["humidity"] = df["humidity"].clip(lower=0, upper=100)
    df["ph"] = df["ph"].clip(lower=0, upper=14)
    df["rainfall"] = df["rainfall"].clip(lower=0)
    return df
