# Gan 2026 Selective Safety-Floor Gate Predeclaration

This is a validation-development predeclaration for the smallest candidate
change suggested by the atlas hard-slice diagnostic. It freezes the candidate
surface, gate variants, reporting contract, and stop rules before any production
policy change or new model call.

- Date: `2026-06-03`
- Split manifest: `gan2026_split_v1`
- Candidate context: `hybrid_parallel_state_candidate_reasoner` with
  deterministic safety-floor final policy
- Source slices:
  `experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json`
- Source diagnostic:
  `experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.json`
- Claim language: Validation-cycle selective-action design, not a benchmark,
  holdout, scorer, prompt, or production-policy claim.

## Hypothesis

The current deterministic safety-floor candidate should remain prediction-bearing
by default. A useful next candidate can expose two narrow ablated alternatives:

1. an LLM candidate-generation sidecar rescue only when the sidecar is scorable,
   evidence-valid, and selected for an explicitly named rescue family;
2. a projection-arbitration variant that prioritizes boundary-state graph nodes
   when saved or regenerated graphs already contain a compatible unknown or
   unresolved-current-state node.

The fixed diagnostic supports projection arbitration more strongly than sidecar
promotion: `boundary_state_priority` corrected 9/85 replay memberships with 0
diagnostic regressions, including 6/6 on the unknown/seizure-free projection
subset. The LLM candidate sidecar showed 6 rescues among 8 scorable sidecars on
the candidate-generation slice, but most candidate-generation rows had no
scorable sidecar rescue and one listed rescue has a label/gold mismatch that
must remain diagnostic until replay accounting explains the scoring path.

## Candidate Variants

| Variant | Prediction-bearing behavior | Status |
| --- | --- | --- |
| `baseline_safety_floor_v2` | Existing deterministic safety-floor replay; deterministic top remains final whenever the adjudicator disagrees. | Comparator only. |
| `projection_boundary_state_priority_gate_v0` | Keep the safety floor, but add an ablated projection sidecar that selects `boundary_state_priority` only on rows with graph nodes of semantic kind `unknown` or unresolved boundary state and a baseline projection that is not already correct on the fixed slice. | First implementation target. |
| `llm_candidate_sidecar_rescue_gate_v0` | Keep the safety floor, but add an ablated LLM-sidecar final candidate only when `llm_candidate_selector_raw` is scorable, evidence/source valid, label-normalized, and belongs to the unknown/seizure-free/current-vs-historical rescue family. | Diagnostic secondary target. |
| `combined_selective_gate_v0` | Compose the projection gate first, then the LLM sidecar rescue only for rows not changed by projection. | Do not promote until both individual gates clear regression accounting. |

## Fixed Surfaces

| Surface | Rows | Required variants |
| --- | ---: | --- |
| `candidate_generation_rescue` | 44 | baseline, LLM sidecar rescue, combined gate |
| `candidate_generation_unknown_seizure_free_boundary` | 26 | baseline, LLM sidecar rescue, combined gate |
| `projection_arbitration` | 11 | baseline, `boundary_state_priority`, competing uncertainty, lowest current frequency, combined gate |
| `projection_unknown_seizure_free_arbitration` | 6 | baseline, `boundary_state_priority`, competing uncertainty, combined gate |

Do not add rows to these surfaces during the first replay. If implementation
requires graph regeneration, report the fixed saved-graph replay and regenerated
graph replay separately.

## Gate Constraints

- Leave `baseline_safety_floor_v2` unchanged and report it in every table.
- Do not inspect locked-test row-level behavior or tune any gate from locked-test
  failures.
- Treat projection variants as deterministic semantic arbitration, not
  normalization.
- Treat LLM sidecar promotion as hybrid clinical selection, not an LLM-first
  result.
- Require exact evidence and valid source ids for any changed final candidate.
- Require changed-label precision, wrong-to-correct, correct-to-wrong, and
  deterministic-correct regression counts by slice and by hidden family.
- Report duplicate row memberships once per slice and once by unique source row.
- Preserve the original final safety-floor label in artifacts even when an
  ablated gate candidate is emitted.

## Implementation Unit

The smallest useful code change is not a broad prompt, schema, scorer, or
deterministic-rule rewrite. Implement a no-call/selective-action replay that
reads the existing validation750 safety-floor artifact and the fixed atlas slice
manifest, then writes ablated score layers:

- `selective_projection_boundary_state_priority`;
- `selective_llm_candidate_sidecar_rescue`;
- `selective_combined_gate`.

The replay should emit JSONL rows plus a summary report with:

- slice-level Purist and Pragmatic counts;
- wrong-to-correct and correct-to-wrong changes versus
  `baseline_safety_floor_v2`;
- deterministic-correct regressions;
- changed-label precision;
- evidence exactness and source-id validity for changed rows;
- fallback or abstention counts;
- row-level "would change" tables for validation rows only.

## Stop Rule

Promote nothing from this predeclaration directly.

Revise the projection gate if `boundary_state_priority` preserves 0
deterministic-correct regressions and keeps changed-label precision high on the
fixed projection slices, but its mechanism appears tied to a Gan-specific label
convention rather than reusable boundary-state arbitration.

Reject projection promotion if any deterministic-correct row becomes wrong, if
evidence/source traces are invalid, or if corrections depend on oracle/gold-aware
node selection.

Keep the LLM sidecar gate diagnostic unless it demonstrates high-precision
rescues on scorable fixed-slice rows and its scoring path explains the row where
the sidecar label is `unknown` but the recorded gold label is
`multiple per 13 month`.

Only after the individual gates clear this fixed-slice accounting may a
combined gate be considered for a separate validation-cycle candidate. Any
locked-test use must follow the frozen-test audit plan and freeze the candidate,
gate, scorer, model, prompts, slice definitions, and inspection policy first.

