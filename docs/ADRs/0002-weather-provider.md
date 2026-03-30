# ADR 0002: Use Open-Meteo for live weather enrichment (v1)

## Context

The recommendation request includes the user’s location. Weather data should be fetched live to compute additional features (e.g., temperature, humidity, rainfall).

## Decision

Use **Open-Meteo** as the default live weather provider for v1.

## Rationale

- No API key required, reducing setup friction.
- Sufficient hourly/daily signals for agricultural proxy features.
- Easy to swap later via a `WeatherProvider` interface.

## Consequences

- Weather client must perform unit normalization and be resilient to API shape changes.
- CI and tests should stub the provider for deterministic tests.

