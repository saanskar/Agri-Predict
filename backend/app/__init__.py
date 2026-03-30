"""
@design-guard
role: Declare backend package boundary.
layer: facade
non_goals:
- Business logic implementation.
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [python_package]
invariants:
- Keep this module import-light.
authority:
  decides: [package_boundary_only]
  delegates: []
extension_policy:
- Add exports only when they reduce coupling for callers.
failure_contract:
- No runtime behavior.
testing_contract:
- No direct tests required.
references:
- docs/ADRs/0001-architecture.md
"""
