"""
@design-guard
role: Standardize model wrapper interfaces (RF/XGB/NN).
layer: service
non_goals:
- Persist artifacts (registry responsibility).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [python_package]
invariants:
- All wrappers expose predict_proba with consistent shapes.
authority:
  decides: [model_wrapper_contracts]
  delegates: []
extension_policy:
- Add models by implementing the same wrapper API and tests.
failure_contract:
- Raise explicit errors for misfit models.
testing_contract:
- Unit tests validate probability output shape and label mapping.
references:
- docs/ADRs/0001-architecture.md
"""
