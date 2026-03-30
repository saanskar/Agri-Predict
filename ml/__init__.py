"""
@design-guard
role: Declare ML package boundary for training and artifact generation.
layer: service
non_goals:
- Serve HTTP requests (backend responsibility).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [python_package]
invariants:
- Training code does not import backend routing/UI modules.
authority:
  decides: [ml_package_boundaries]
  delegates: []
extension_policy:
- Add new model implementations behind a common interface.
failure_contract:
- Training failures should be explicit exceptions.
testing_contract:
- Unit tests validate feature pipeline and model wrapper contracts.
references:
- docs/ADRs/0001-architecture.md
"""
