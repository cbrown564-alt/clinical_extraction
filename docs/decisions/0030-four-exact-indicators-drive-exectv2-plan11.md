# Four Exact Indicators Drive ExECTv2 Plan 11

Date: 2026-06-19

## Status

Accepted.

## Decision

The current ExECTv2 Plan 11 optimization target is restricted to four exact
indicators:

- `Diagnosis`
- `SeizureFrequency`
- `Prescription`
- `Investigations`

Success means each of those four indicators clears core F1 `> 0.900` on the
predeclared development headline before any holdout or benchmark-comparable
claim is made.

The target architecture is a hybrid pipeline with one LLM call per letter for
candidate generation and candidate selection. Deterministic code may normalize,
repair format, project attributes/CUIs, enforce evidence validity, and produce
the final benchmark-facing representation. Any deterministic step that changes
the selected clinical fact, state, or family membership is a prediction-bearing
hybrid rule and must be named, tested, and ablated rather than described as
mere normalization.

## Scope

Error analysis, promotion gates, status updates, and new experiment artifacts
must focus on the four exact indicators above. Other ExECT families remain
diagnostic unless a later ADR expands the target surface.

The current project status makes the reason concrete: the routed four-family
development surface remains below target, with Diagnosis, SeizureFrequency,
Prescription, and Investigations all below the desired `> 0.900` core-F1 bar.
The next useful work is therefore not another broad all-entity pass; it is a
four-family hybrid assembly and error-analysis loop that measures only the
target indicators and preserves component ownership.

## Consequences

- `EpilepsyCause`, `PatientHistory`, `BirthHistory`, `Onset`, and
  `WhenDiagnosed` should not consume optimization time in this phase.
- Reports should lead with the four target indicators and an overall
  four-family micro-average only as a companion summary.
- Single-call hybrid runs must preserve raw LLM-selected candidates separately
  from deterministic normalization/projection outputs.
- Projection gains can count toward the hybrid artifact only when the report
  names which deterministic family produced them and whether the raw LLM output
  would have scored differently.
- A result that clears `> 0.900` only through unablated deterministic semantic
  repair is a hybrid development artifact, not a clean LLM-first result.

