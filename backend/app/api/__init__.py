"""
@design-guard
role: Define the backend API package boundary.
layer: facade
non_goals:
- Contain business logic; routes delegate to services.
boundaries:
  depends_on_layers: [facade, service, domain]
  exposes: [python_package]
invariants:
- Keep modules small and focused by endpoint group.
authority:
  decides: [routing_structure]
  delegates: []
extension_policy:
- Add new routers per feature boundary.
failure_contract:
- No runtime behavior.
testing_contract:
- Covered by integration tests through FastAPI TestClient.
references:
- docs/ADRs/0001-architecture.md
"""
