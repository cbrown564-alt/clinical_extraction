# Gan 2026 Selective Safety-Floor Gate v0 Validation-Cycle Manifest

- Date: `2026-06-03`
- Candidate name: `selective_safety_floor_gate_v0`
- Candidate seed: `combined_selective_gate_v0`
- Split manifest: `gan2026_split_v1`
- Development surface: validation only
- Planned mode: no-call replay over saved validation artifacts
- Claim language: validation-cycle hybrid selective-action candidate; not a
  benchmark, holdout, production-policy, or LLM-first claim.

## Decision

Freeze `selective_safety_floor_gate_v0` as a separately named validation-cycle
candidate seeded by the fixed-slice `combined_selective_gate_v0` replay.

This freeze allows a validation-only replay with unchanged source artifacts,
gate order, scorer, repair policy, and inspection policy. It does not promote
the gate into production behavior and does not authorize locked-test use.

## Rationale

The fixed-slice selective safety-floor replay cleared the minimum accounting
needed to seed a named candidate:

- projection-boundary arbitration rescued 5/11 Purist misses on
  `projection_arbitration` and 4/6 on
  `projection_unknown_seizure_free_arbitration`;
- LLM sidecar rescue corrected 6/44 Purist misses on
  `candidate_generation_rescue` and 6/26 on
  `candidate_generation_unknown_seizure_free_boundary`;
- the combined gate recorded 0 deterministic-correct regressions across all 87
  fixed-slice memberships;
- changed rows had exact evidence and valid source ids.

The result remains validation-derived and no-call. One sidecar scoring path
where `unknown` counts Purist-correct against `multiple per 13 month` must stay
visible as an attribution caveat until the replay report explains the scoring
convention row by row.

## Frozen Inputs

- Source validation artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Fixed-slice replay:
  `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.json`
- Fixed-slice replay rows:
  `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.jsonl`
- Fixed-slice replay report:
  `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.md`
- Gate predeclaration:
  `experiments/gan2026_selective_safety_floor_gate_predeclaration_2026-06-03.json`
- Hard-slice manifest:
  `experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json`
- Split manifest:
  `data/Gan (2026)/splits/gan2026_split_v1.json`

Do not change the source JSONL, split membership, slice membership, scorer
mapping, repair policy, gate order, fallback behavior, source-id validity rules,
or exact-evidence rules before the validation-cycle replay.

## Frozen Candidate Policy

`selective_safety_floor_gate_v0` is a hybrid deterministic-safety-floor
candidate with two selective sidecars. It composes the gates in this exact
order:

1. Start from `baseline_safety_floor_v2`.
2. Apply `projection_boundary_state_priority_gate_v0`.
3. Apply `llm_candidate_sidecar_rescue_gate_v0` only if the projection gate did
   not change the row.
4. Preserve the original baseline safety-floor label in the artifact for every
   row, even when the selective candidate emits a changed final label.

The prediction-bearing candidate layer is named
`selective_safety_floor_gate_v0`. The component diagnostic layers remain:

- `baseline_safety_floor_v2`;
- `projection_boundary_state_priority_gate_v0`;
- `llm_candidate_sidecar_rescue_gate_v0`;
- `combined_selective_gate_v0`.

## Gate Definitions

### Projection Boundary-State Priority

Fire only when all conditions hold:

- saved state-graph data contain an asserted current unknown or unresolved
  boundary-state node;
- the boundary-state projection is scorable;
- selected evidence is exact;
- selected source ids are valid;
- the row is not made wrong from a deterministic-correct baseline.

Treat this as deterministic semantic arbitration, not normalization and not an
LLM-first decision.

### LLM Candidate Sidecar Rescue

Fire only when all conditions hold:

- `llm_candidate_selector_raw` is scorable after the frozen label-normalization
  path used by the replay;
- the sidecar selected evidence is exact;
- selected source ids are valid;
- the row belongs to the frozen rescue families:
  `unknown_boundary`, `seizure_free_duration`, or `current_vs_historical`;
- the projection gate did not already change the row;
- the row is not made wrong from a deterministic-correct baseline.

Treat this as hybrid clinical selection under deterministic safety-floor
constraints, not an LLM-first result.

## Frozen Scorer And Repair Policy

Use the same scorer and repair policy as the fixed-slice replay:

- split manifest: `gan2026_split_v1`;
- primary scoring contract: Gan 2026 Purist and Pragmatic category correctness;
- baseline layer: deterministic safety-floor v2;
- changed-label accounting versus `baseline_safety_floor_v2`;
- exact selected-evidence and selected-source-id checks required for changed
  candidate rows;
- no new scorer normalization, semantic repair, deterministic adapter, prompt,
  schema, model, graph-building, or source-artifact regeneration.

If any implementation requires a scorer, repair, graph, schema, or source
artifact change, stop and write a new validation-cycle manifest.

## Validation Replay Surface

The validation-cycle replay may report:

- full validation750 aggregate over the saved source artifact;
- fixed hard-slice summaries using the frozen hard-slice manifest;
- unique-source-row and duplicate-membership accounting;
- hidden-family summaries from the frozen atlas labels;
- row-level would-change tables for validation rows only.

The replay must not inspect train rows or locked-test row-level behavior.

## Required Reporting

Report, for `selective_safety_floor_gate_v0` and each diagnostic component
layer:

- row count and unique source-row count;
- Purist correct and Pragmatic correct;
- changed rows versus `baseline_safety_floor_v2`;
- wrong-to-correct and correct-to-wrong transitions;
- deterministic-correct regressions;
- changed-label precision;
- exact-evidence count for changed rows;
- valid-source-id count for changed rows;
- fallback or abstention count;
- hidden-family summaries;
- row-level validation-only would-change tables.

The report must call out any row where the prediction label, scorer category,
and gold label have a non-obvious relationship, including the
`unknown` versus `multiple per 13 month` convention.

## Inspection Policy

Validation row-level inspection is allowed only for:

- rows changed by `selective_safety_floor_gate_v0`;
- rows changed by an individual component gate;
- any deterministic-correct regression;
- any correct-to-wrong transition;
- any changed row without exact evidence or valid source ids;
- any fallback or abstention whose reason affects promotion language;
- the known `unknown` versus `multiple per 13 month` scoring-convention row.

Do not inspect locked-test row-level behavior. Any locked-test use requires a
separate frozen-test audit plan that freezes candidate, gate, scorer, source
artifacts, slice definitions, and inspection policy first.

## Stop Rules

### Promote Within Validation Cycle

Promote to the next validation-cycle step only if all are true:

- `selective_safety_floor_gate_v0` has 0 deterministic-correct regressions;
- correct-to-wrong transitions are 0 or fully explained as scorer-equivalent
  nonsemantic changes;
- changed-label precision remains at least 0.95 on fixed hard slices;
- every changed row has exact evidence and valid source ids;
- projection and LLM-sidecar contributions remain separately attributable;
- the known scoring-convention caveat is documented row by row;
- the replay report preserves baseline and component-layer accounting.

### Revise

Revise the candidate if:

- improvements are concentrated in a Gan-specific convention rather than a
  reusable boundary-state or clinical-selection mechanism;
- the LLM sidecar mostly abstains outside the already inspected hard slices;
- the candidate improves fixed slices but does not produce interpretable
  full-validation changed-label accounting;
- the candidate depends on ambiguous source provenance or weak sidecar
  normalization.

### Reject

Reject the candidate if:

- any deterministic-correct row becomes wrong without an explicitly accepted
  scorer-equivalent explanation;
- any changed row lacks exact evidence or valid source ids;
- any gate uses gold labels, oracle correctness, or locked-test behavior;
- a scorer, repair, graph, prompt, schema, model, or source-artifact change is
  required to reproduce the result under this manifest.

## Locked-Test Policy

Locked test is out of scope for this manifest. A future holdout run is allowed
only after a separate frozen-test audit plan is written and the validation-cycle
candidate is frozen again with all implementation and inspection choices fixed.
