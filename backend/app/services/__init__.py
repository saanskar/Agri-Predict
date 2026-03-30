"""
@design-guard
role: Group backend service-layer modules (weather + inference).
layer: service
non_goals:
- Define HTTP routes (facade responsibility).
boundaries:
  depends_on_layers: [service, domain]
  exposes: [python_package]
invariants:
- Services are dependency-injected and unit-testable.
authority:
  decides: [service_layer_packaging]
  delegates: []
extension_policy:
- Add new services behind interfaces (Protocols) to preserve DI.
failure_contract:
- No runtime behavior.
testing_contract:
- Services should have unit tests via their interfaces.
references:
- docs/ADRs/0001-architecture.md
"""
