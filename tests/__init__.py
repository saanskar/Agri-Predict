"""
@design-guard
role: Test package boundary (unit + integration/system tests).
layer: service
non_goals:
- Production code.
boundaries:
  depends_on_layers: [service, domain, facade, ui]
  exposes: [python_package]
invariants:
- Tests should be deterministic and avoid live network calls.
authority:
  decides: [test_packaging]
  delegates: []
extension_policy:
- Add tests per module boundary; prefer interface-driven tests.
failure_contract:
- Fail fast with clear assertions.
testing_contract:
- N/A (this is the tests layer).
references:
- docs/ADRs/0001-architecture.md
"""
