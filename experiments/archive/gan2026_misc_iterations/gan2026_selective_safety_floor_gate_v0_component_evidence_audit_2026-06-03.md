# Gan 2026 Selective Safety-Floor Gate v0 Component Evidence Audit

Post-hoc component-evidence interpretation of the frozen validation replay and
frozen-test first readout for `selective_safety_floor_gate_v0`.

This is an aggregate and predeclared-slice audit only. It does not inspect
locked-test row-level failures for tuning.

## Claim Boundary

- Candidate: `selective_safety_floor_gate_v0`
- Comparator: `baseline_safety_floor_v2`
- Pipeline family: hybrid deterministic-safety-floor
- Split manifest: `gan2026_split_v1`
- Validation distribution: `validation750`, no-call replay from saved artifacts
- Frozen-test distribution: `test450`, no-call first readout under the frozen
  audit manifest
- Model/replay status: saved-output replay; no new model calls
- Prediction-bearing layer: `selective_safety_floor_gate_v0`
- Component layers: `projection_boundary_state_priority_gate_v0`,
  `llm_candidate_sidecar_rescue_gate_v0`, `combined_selective_gate_v0`
- Repair policy: preserve baseline label unless a gated projection or LLM
  sidecar rescue changes the row with exact evidence and valid source ids

On `test450` under `gan2026_split_v1`,
`selective_safety_floor_gate_v0` is a hybrid deterministic-safety-floor result.
It improves `baseline_safety_floor_v2` by 8 Purist rows: 351/450 versus
343/450 Purist and 361/450 versus 354/450 Pragmatic. Changed rows had 14/14
exact evidence and 14/14 valid source ids. Correct-to-wrong changes: 0.
Deterministic-correct regressions: 0. This supports a frozen local
generalization audit for the selective safety-floor gate; it does not support
LLM-first, production-policy, benchmark-comparable, or tuning claims.

## Score-Layer Ladder

| Distribution | Layer | Rows | Purist | Pragmatic | Changed | Wrong-to-correct | Correct-to-wrong | Precision | Exact changed evidence | Valid source ids | Deterministic regressions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| validation750 | baseline_safety_floor_v2 | 750 | 697 | 704 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| validation750 | projection_boundary_state_priority_gate_v0 | 750 | 682 | 691 | 13 | 5 | 0 | 1.0000 | 13 | 13 | 0 |
| validation750 | llm_candidate_sidecar_rescue_gate_v0 | 750 | 704 | 711 | 10 | 7 | 0 | 1.0000 | 10 | 10 | 0 |
| validation750 | selective_safety_floor_gate_v0 | 750 | 708 | 715 | 21 | 11 | 0 | 1.0000 | 21 | 21 | 0 |
| test450 | baseline_safety_floor_v2 | 450 | 343 | 354 | 0 | 0 | 0 |  | 0 | 0 | 0 |
| test450 | projection_boundary_state_priority_gate_v0 | 450 | 345 | 357 | 9 | 6 | 0 | 1.0000 | 9 | 9 | 0 |
| test450 | llm_candidate_sidecar_rescue_gate_v0 | 450 | 346 | 356 | 6 | 3 | 0 | 0.7500 | 6 | 6 | 0 |
| test450 | selective_safety_floor_gate_v0 | 450 | 351 | 361 | 14 | 8 | 0 | 0.8889 | 14 | 14 | 0 |

The rejected diagnostic layers remain important negative controls. On `test450`,
`competing_frequency_uncertainty` caused 67 deterministic-correct regressions
and `lowest_current_frequency` caused 50, despite exact evidence. The promoted
candidate owes its safety to the selective gate, not to these broad projection
policies.

## Component Evidence Matrix

| Clinical subproblem | Evidence distribution | Component owner | Decision effect | Validation evidence | Frozen-test evidence |
| --- | --- | --- | --- | --- | --- |
| `temporal_selection` / current-vs-historical | validation750, test450 predeclared markers | `graph_projection`, `llm_clinical_selection`, `safety_floor` | Gated projection and sidecar rescue change only rows that survive exact-evidence/source-id gates; otherwise baseline is preserved. | 8 changed rows in the validation current-vs-historical family, 6 wrong-to-correct, 0 correct-to-wrong. | All 14 changed test rows are in the current-state and historical-or-negated marker slices, with 8 wrong-to-correct and 0 correct-to-wrong. |
| `seizure_free_boundary` | validation750 hidden family, test gold-kind slices | `llm_clinical_selection`, `graph_projection`, `safety_floor` | Sidecar rescues short seizure-free/unknown boundary cases; projection handles selected boundary states; safety floor blocks broad overreach. | 10 changed validation rows, 8 wrong-to-correct, 0 correct-to-wrong. | Gold-kind seizure-free: 3 changed, 2 wrong-to-correct, 0 correct-to-wrong. Boundary unknown: 3 changed, 2 wrong-to-correct, 0 correct-to-wrong. |
| `uncertainty_boundary` | validation750 hidden family, test unknown/unresolved slices | `graph_projection`, `llm_clinical_selection`, `safety_floor` | Candidate preserves unknown/unresolved labels only when gated evidence supports the change. | 11 changed validation rows, 9 wrong-to-correct, 0 correct-to-wrong. | Gold-kind unknown: 3 changed, 2 wrong-to-correct. Gold-kind unresolved_multiple: 4 changed, 3 wrong-to-correct. No correct-to-wrong changes. |
| `competing_event_selection` | validation750 hidden family | `llm_clinical_selection`, `graph_projection` | Changes competing-semiology rows only through gated projection or sidecar rescue. | 6 changed validation rows, 5 wrong-to-correct, 0 correct-to-wrong. | Frozen-test artifact does not expose hidden-family tags for this family; use only predeclared marker/gold-kind slices. |
| `rate_denominator` | validation750 hidden family, test frequency/numeric-rate slices | `graph_projection`, `llm_clinical_selection` | Helps some rate bucket/denominator rows but is weaker than boundary families. | 3 changed validation rows, 2 wrong-to-correct, 0 correct-to-wrong. | Gold-kind frequency: 4 changed, 1 wrong-to-correct, 0 correct-to-wrong; precision 0.5000. |
| `cluster_or_diary_aggregation` | validation750 hidden family, test cluster marker | `llm_clinical_selection`, `graph_projection` | Cluster/diary gains are real but mixed on frozen test. | Cluster burden: 2 changed, 1 wrong-to-correct. Diary/log aggregation: 2 changed, 1 wrong-to-correct. | Text marker cluster_language: 9 changed, 5 wrong-to-correct, 0 correct-to-wrong; precision 0.8333. |
| `benchmark_formatting` | validation750 caveat rows | `benchmark_format`, `safety_floor` | Some apparent gains rely on Gan scorer category conventions and must not be described as exact clinical-label normalization. | 3 changed validation rows in `benchmark_format_convention`, 2 wrong-to-correct, 0 correct-to-wrong; one known caveat maps `unknown` to the same scorer category as `multiple per 13 month`. | No frozen-test scoring-convention caveat is recorded in the first-readout summary. |

## LLM Delta Accounting

Against `baseline_safety_floor_v2`, the final validation replay changes 21 rows:
11 wrong-to-correct, 0 correct-to-wrong, and 21/21 changed rows with exact
evidence and valid source ids. The final frozen-test readout changes 14 rows:
8 wrong-to-correct, 0 correct-to-wrong, and 14/14 changed rows with exact
evidence and valid source ids.

The LLM-owned sidecar is a small but positive component, not the whole result.
On `validation750`, `llm_candidate_sidecar_rescue_gate_v0` changes 10 rows with
7 wrong-to-correct, 0 correct-to-wrong, and 10/10 exact evidence. On `test450`,
it changes 6 rows with 3 wrong-to-correct, 0 correct-to-wrong, 6/6 exact
evidence, and changed-label precision 0.7500. The projection layer contributes
the other major decision effect: 9 changed frozen-test rows, 6 wrong-to-correct,
0 correct-to-wrong, and 9/9 exact evidence.

Because the final policy uses projection first and sidecar rescue second, the
candidate should be credited as hybrid. It is not valid to describe the 8-row
holdout net gain as an LLM-only improvement.

## Evidence And Regression Gates

| Gate | Validation750 | Test450 | Status |
| --- | ---: | ---: | --- |
| Exact changed-row evidence | 21/21 | 14/14 | Pass |
| Valid changed-row source ids | 21/21 | 14/14 | Pass |
| Correct-to-wrong changes | 0 | 0 | Pass |
| Deterministic-correct regressions | 0 | 0 | Pass |
| Same-raw-output replay | saved-output no-call replay | saved-output no-call first readout | Pass |
| First-failure owner for residual misses | not recorded in replay summary | not recorded in replay summary | Instrumentation gap |
| Frozen-test hidden-family tags | not applicable | not exposed beyond predeclared slices/markers | Instrumentation gap |

The evidence gates support interpreting changed-row precision. They do not
support diagnosing every residual frozen-test miss by first-failure owner.

## Hidden-Family And Slice Readout

Validation changed-row families support the mechanism story: gains concentrate
in uncertainty boundary, seizure-free duration, current-vs-historical, and
competing-semiology rows, with no deterministic-correct regressions.

Frozen-test interpretation must stay at the predeclared slice level. The
strongest frozen-test signals are:

| Predeclared test slice | Rows | Purist | Pragmatic | Changed | Wrong-to-correct | Correct-to-wrong | Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `projection_gate:fired` | 9 | 9 | 9 | 9 | 6 | 0 | 1.0000 |
| `llm_sidecar_gate:fired` | 6 | 3 | 3 | 6 | 3 | 0 | 0.7500 |
| `gold_kind:unknown` | 60 | 47 | 47 | 3 | 2 | 0 | 1.0000 |
| `gold_kind:unresolved_multiple` | 26 | 22 | 22 | 4 | 3 | 0 | 1.0000 |
| `gold_kind:seizure_free` | 67 | 40 | 40 | 3 | 2 | 0 | 1.0000 |
| `gold_kind:frequency` | 281 | 226 | 236 | 4 | 1 | 0 | 0.5000 |
| `text_marker:cluster_language` | 262 | 205 | 211 | 9 | 5 | 0 | 0.8333 |

This pattern is promotion-relevant for the frozen candidate as an audit result:
the selective gate preserves the zero-regression property across broad holdout
rows while allowing a small number of evidence-valid corrections. It is not a
new development surface.

## Decision

`selective_safety_floor_gate_v0` passes the component-evidence audit for the
claim it is allowed to make: a frozen local generalization audit of a hybrid
deterministic-safety-floor selective-action candidate.

It does not pass as an LLM-superiority claim. The sidecar's positive delta is
real and evidence-valid, but final performance also depends on deterministic
graph projection and safety-floor fallback. The next useful LLM-heavy work
remains the validation25 typed-operations smoke, where candidate generation,
selected facts, operands, evidence ids, and graph projection side-cars can be
attributed before any larger validation run.
