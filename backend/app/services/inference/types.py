"""
@design-guard
role: Define inference-domain value objects for recommendations.
layer: domain
non_goals:
- HTTP response formatting.
boundaries:
  depends_on_layers: [domain]
  exposes: [CropRecommendation]
invariants:
- Probabilities are within [0,1] and sortable descending.
authority:
  decides: [recommendation_value_object_shape]
  delegates: []
extension_policy:
- Add fields only if stable and model-agnostic.
failure_contract:
- No runtime behavior.
testing_contract:
- Unit tests validate sorting/serialization at service boundaries.
references:
- docs/ADRs/0001-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CropRecommendation:
    crop: str
    probability: float
