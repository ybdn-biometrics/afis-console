# Agent Instructions (Read Before Modifying Code)

## Non-Negotiable Rules

- Do not move or rename public modules without updating tests.
- Do not introduce new dependencies without explicit justification.
- Do not change data formats without updating tests and documentation.
- Do not modify public APIs without version bump and ADR.

## Repository Role

This repository has a clearly defined role in YBDN Biometrics.
Respect architectural boundaries defined in the global vision repository.

## Dependency Rules

- Apps may depend on core.
- Core must not depend on apps.
- Shared code must not be duplicated.

## Mandatory Checks Before Commit

- Tests must pass.
- Lint must pass.
- Update CHANGELOG if user-visible.
- Update documentation if behavior changes.

## Coding Standards

- Use type hints.
- Keep functions small and deterministic.
- Prefer pure functions in parsing and analysis layers.
- No UI logic inside domain modules.
