# 0001: Gan First, Small Core

Date: 2026-05-31


> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

## Decision

Prioritize the Gan 2026 seizure-frequency benchmark while creating only the core abstractions needed to keep the code understandable and extensible.

## Context

The project is intended to become a modular clinical extraction package, but the immediate research question is practical: what LLM-with-rules pipeline can beat the Gan 2026 benchmark, especially purist F1?

## Consequences

- Shared `core` modules are deliberately thin.
- Gan-specific policy lives under `tasks/seizure_frequency/gan2026`.
- By default, a new dataset starts with task-local behavior. Factor shared code
  after the same behavior recurs across tasks.
- Error analysis and notebooks are first-class project outputs.

