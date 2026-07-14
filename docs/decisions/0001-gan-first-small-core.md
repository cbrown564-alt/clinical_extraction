# 0001: Gan First, Small Core

Date: 2026-05-31

## Decision

Prioritize the Gan 2026 seizure-frequency benchmark while creating only the core abstractions needed to keep the code understandable and extensible.

## Context

The project is intended to become a modular clinical extraction package, but the immediate research question is practical: what LLM-with-rules pipeline can beat the Gan 2026 benchmark, especially purist F1?

## Consequences

- Shared `core` modules are deliberately thin.
- Gan-specific policy lives under `tasks/seizure_frequency/gan2026`.
- Future datasets must copy, then factor shared behavior only after repetition is real.
- Error analysis and notebooks are first-class project outputs.

