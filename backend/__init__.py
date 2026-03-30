"""
@design-guard
role: Declare backend top-level package boundary.
layer: facade
non_goals:
- Contain implementation logic.
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [python_package]
invariants:
- Avoid heavy imports to keep startup fast.
authority:
  decides: [package_boundary_only]
  delegates: []
extension_policy:
- Keep exports minimal.
failure_contract:
- No runtime behavior.
testing_contract:
- No direct tests required.
references:
- docs/ADRs/0001-architecture.md
"""
