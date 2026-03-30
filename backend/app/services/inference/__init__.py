"""
@design-guard
role: Group inference service interfaces and implementations.
layer: service
non_goals:
- Training models (ml package responsibility).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [InferenceService]
invariants:
- Inference consumes validated inputs only.
authority:
  decides: [inference_interface_contract]
  delegates: []
extension_policy:
- Extend via new implementations or new domain value objects, not ad-hoc dicts.
failure_contract:
- Surface failures as typed exceptions; avoid leaking low-level errors.
testing_contract:
- Unit tests should validate deterministic ranking given fixed model artifacts.
references:
- docs/ADRs/0001-architecture.md
"""
