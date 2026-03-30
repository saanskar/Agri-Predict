"""
@design-guard
role: UI component package boundary for Streamlit custom components.
layer: ui
non_goals:
- Business logic; components should only provide UI-side capabilities.
boundaries:
  depends_on_layers: [ui]
  exposes: [python_package]
invariants:
- Components must be optional enhancements and degrade gracefully.
authority:
  decides: [component_packaging]
  delegates: []
extension_policy:
- Add new components in separate modules with explicit contracts.
failure_contract:
- Components must surface errors to callers without crashing the app.
testing_contract:
- Keep components thin; system behavior primarily validated via API tests.
references:
- docs/ADRs/0001-architecture.md
"""
