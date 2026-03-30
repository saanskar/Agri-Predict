"""
@design-guard
role: Host dataset files and loader utilities for training.
layer: service
non_goals:
- Store secrets or credentials.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [python_package]
invariants:
- Training data access is local and deterministic for CI.
authority:
  decides: [dataset_packaging]
  delegates: []
extension_policy:
- Add new datasets via explicit loader functions, not implicit downloads.
failure_contract:
- Loader raises on missing/invalid data.
testing_contract:
- Unit tests validate schema expectations.
references:
- docs/ADRs/0001-architecture.md
"""
