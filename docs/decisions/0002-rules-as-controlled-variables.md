# 0002: Deterministic Rules As Controlled Variables

Date: 2026-05-31

## Decision

Treat deterministic preprocessing, normalization, temporal reasoning helpers, validation, and repair logic as explicit experimental variables.

## Context

Prior clinical extraction systems often rely on some rules even when the headline method is an LLM. Those rules can be underreported, difficult to reproduce, or mixed together in ways that obscure what actually improves performance.

For this project, deterministic rules are part of the scientific contribution. They must be grouped into clinically meaningful categories and evaluated through ablation studies.

## Consequences

- Rules must carry a category such as general, epilepsy clinical, seizure-frequency, Gan-specific, or benchmark-formatting.
- Specific rules can be useful, but they must be named as specific rather than disguised as general clinical logic.
- Experiments must report the effect of adding/removing rule categories.
- Rule code must be structured for readability and tests, not only compact regex matching.

