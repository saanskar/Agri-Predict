# ADR 0003: Enforce design-guard headers in every code file

## Context

As the codebase grows, automated guardrails are needed to prevent architectural drift and keep responsibilities/boundaries explicit.

## Decision

Every Python source file must begin with a docstring containing a `@design-guard` block.

CI will fail if any checked `.py` file does not include `@design-guard` within the first 50 lines.

## Rationale

- Makes boundaries explicit for humans and automated reviewers.
- Encourages SOLID separation and DI-friendly interfaces.
- Prevents “random helper” sprawl.

## Consequences

- All new files must include a guard from day one.
- Generated/vendor code should be excluded explicitly if introduced later.

