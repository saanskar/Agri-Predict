"""
@design-guard
role: Provide weather enrichment interfaces and implementations.
layer: service
non_goals:
- Couple API handlers to a specific weather provider.
boundaries:
  depends_on_layers: [service, domain]
  exposes: [WeatherProvider, WeatherSnapshot]
invariants:
- Weather features must be unit-normalized and explicit.
authority:
  decides: [weather_interface_contract]
  delegates: [http_fetching_to_provider_impls]
extension_policy:
- Add new providers by implementing WeatherProvider.
failure_contract:
- Surface failures as typed exceptions; do not return partial data silently.
testing_contract:
- Unit tests should stub provider responses for determinism.
references:
- docs/ADRs/0002-weather-provider.md
"""
