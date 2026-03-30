"""
@design-guard
role: Declare UI package boundary.
layer: ui
non_goals:
- Provide domain logic; keep UI thin.
boundaries:
  depends_on_layers: [ui]
  exposes: [python_package]
invariants:
- UI communicates via backend HTTP API only.
authority:
  decides: [ui_packaging]
  delegates: []
extension_policy:
- Prefer composition over hidden side effects.
failure_contract:
- No runtime behavior.
testing_contract:
- UI is intentionally thin; major behavior covered through API tests.
references:
- docs/ADRs/0001-architecture.md
"""
