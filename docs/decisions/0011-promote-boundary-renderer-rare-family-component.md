# 0011: Promote Boundary/Renderer As A Rare-Family Component

Date: 2026-06-05

## Status

Accepted.

## Decision

Promote the boundary/benchmark typed-event layer as a bounded rare-family
component for eligible Gan 2026 boundary and benchmark-rendering cases.

This promotion covers the typed-event contract, benchmark renderer, and
selector-precision-revised boundary projection behavior represented by:

- `boundary_event_contract_v1`
- `boundary_event_validation_panel_v1`
- `benchmark_renderer_fixture_v1`
- `h7_minimal_pair_panel_v1`
- `boundary_selector_precision_revision_v1`

The component may be included in future staged hybrid assemblies only when its
eligibility and suppression rules apply. It must keep component-owner
attribution explicit and must not be reported as a whole-pipeline promotion or
as evidence that the validation-test aggregate gap is solved.

## Context

The initial Stage 2 interpretation treated low exposure as a promotion blocker.
That was too strict for this mechanism. Boundary and benchmark-rendering cases
are intrinsically rare in Gan 2026, so a broad coverage threshold asks the
component to solve rows outside its clinical family.

The revised question is:

```text
When an eligible boundary or benchmark-rendering case is present, does the
typed-event component behave safely, preserve exact evidence, and avoid
deterministic-correct regressions?
```

On the validation typed panel, the precision-revised selector leaves 28
prediction-bearing selected rows with 6 W->C, 0 C->W, 0 H6 regressions, and 0
source-note-text rows. The synthetic contract and H7 minimal-pair panel preserve
typed state and exact evidence. The renderer fixture preserves clinical state
while exposing benchmark-format rule ids and scorer-sentinel use.

## Promotion Boundary

Allowed claims:

- The component has validation-development support on eligible boundary and
  benchmark-rendering cases.
- The benchmark renderer is a benchmark-format component when clinical state is
  frozen.
- The boundary projection component is a deterministic/hybrid clinical-boundary
  component and must be credited as such.
- Low aggregate coverage is an expected property of the target family, not a
  reason to reject the component.

Disallowed claims:

- No benchmark-comparable claim is authorized.
- No locked-test row-level tuning or holdout-facing use is authorized.
- The component does not close the aggregate validation-test gap by itself.
- The component is not evidence that broad structured projection should be
  promoted.
- Renderer behavior must not be described as LLM clinical reasoning.

## Required Guardrails

- Use `gan2026_split_v1` split discipline.
- Keep H5 repair policy fixed when evaluating this component.
- Keep boundary/renderer effects separate from semantic repair and action-policy
  widening.
- Attach H6/H9 action sidecars and H10 provenance before interpreting deltas in
  any future candidate assembly.
- Preserve exact-evidence and source-id accounting for changed rows.
- Suppress protected last-event current seizure-free overrides and
  unknown/no-reference sentinel churn as in
  `boundary_selector_precision_revision_v1`.
- Attribute benchmark-format rendering separately from clinical boundary
  projection.

## Consequences

- Future architecture diagrams should show the boundary/renderer typed-event
  layer as a promoted bounded component, not as a rejected branch.
- Historical artifacts remain accurate: `boundary_renderer_component_ablation_v1`
  was rejected before selector precision revision because it had one H6
  regression. The promotion relies on the later precision revision and the
  decision that rarity-aware component support is the right gate.
- Whole-pipeline promotion remains blocked until a frozen holdout-facing
  protocol is authorized.

## Related Artifacts

- `PROJECT_STATUS.md`
- ``
- `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`
- `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`
- `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json`
- `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json`
- `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json`
- `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json`
