"""
@design-guard
role: Host repository maintenance scripts (CI helpers, checks).
layer: service
non_goals:
- Application runtime logic.
boundaries:
  depends_on_layers: [service]
  exposes: [python_package]
invariants:
- Scripts remain deterministic and CI-friendly.
authority:
  decides: [script_packaging]
  delegates: []
extension_policy:
- Add new scripts as standalone modules with clear I/O contracts.
failure_contract:
- Scripts must exit non-zero on failure.
testing_contract:
- Lightweight unit tests can be added when logic becomes non-trivial.
references:
- docs/ADRs/0003-design-guards.md
"""
