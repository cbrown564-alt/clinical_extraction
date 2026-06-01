# 0004: Gan 2026 Package Organization By Research Boundary

Date: 2026-06-01

## Decision

Organize `tasks/seizure_frequency/gan2026` by research and ownership boundary
rather than keeping every split-out component in one flat package.

The top-level package should keep only the small public task surface and stable
entry points. Implementation modules should move into subpackages that make
attribution boundaries visible:

- `contract`: label grammar, gold policy, schema repair, and benchmark-facing
  repair.
- `deterministic`: rules-only extraction, candidate construction, selection,
  rule metadata, and deterministic helper modules.
- `selected_evidence`: deterministic derivation from model-selected evidence.
- `llm`: LLM-only pipeline implementations and LLM structured repair families.
- `hybrid`: pipelines where deterministic rules and LLM components both perform
  semantic work.
- `reports`: Markdown/report rendering and shared report helpers.
- `experiments`: artifact I/O, run metadata, run registry, ablations, prompt
  devset generation, and error-analysis utilities.
- `cli`: routine experiment command modules.

The current flat module names may be kept briefly as compatibility wrappers
while imports, console scripts, tests, and documentation are moved. Compatibility
wrappers should be transitional, not a second permanent API.

## Context

The thermonuclear review prompted a successful split of large behavior files
such as `normalize.py`, `pipeline_v1.py`, and LLM runner modules. That improved
local maintainability, but left the Gan 2026 package with many small modules in
one directory. A flat package now hides the boundaries the research depends on:
rules-only behavior, LLM-only behavior, hybrid adjudication, schema repair,
selected-evidence derivation, benchmark formatting, reports, and run artifacts.

The project already treats these boundaries as scientifically meaningful. They
determine whether a metric should be described as deterministic, LLM-only,
clean scorer-facing, selected-evidence-derived, or hybrid. The package layout
should make that ownership obvious before someone opens individual files.

## Consequences

- New Gan 2026 modules should be placed in the subpackage that owns their
  research role.
- Imports should prefer the new subpackage paths once the reorganization lands.
- Top-level `gan2026` modules should remain only when they are stable public
  task contracts, thin entry points, or temporary compatibility shims.
- `normalize.py`, `evaluate.py`, `data.py`, and `labels.py` may remain top-level
  until their public-contract status is clarified.
- The reorganization must be behavior-preserving first: update imports, run the
  focused tests for moved modules, then run full pytest, Ruff, and mypy.
- Moving code must not change scoring, repair semantics, split policy, prompt
  behavior, artifact contents, or claim language.
- Future docs should describe pipeline families in terms of these package
  boundaries, not in terms of historical file locations.
