# Gan 2026 Next-Task Review: Month-Bucket Gate And LLM-Heavy V1

Date: 2026-06-02

This review completes the immediate next step from `PROJECT_STATUS.md`.
It is a validation-cycle diagnostic review only. It does not promote a
projection policy, scorer normalization change, LLM-heavy candidate, or
holdout-facing claim.

## Artifacts Reviewed

- `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.jsonl`
- `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.json`
- `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`
- `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.md`

## Month-Bucket Duration Gate Decision

Gated `month_bucket_duration_selection_v1` preserved all 18/18 enriched
duration target corrections and left 0 already-correct regression rows changed.
The broader hard-slice regression panel still had four changed labels:

| Row | Gold | Baseline | Month-bucket | Tags |
| ---: | --- | --- | --- | --- |
| 2907 | seizure free for 6 month | seizure free for multiple year | seizure free for 6 months | cluster_or_diary, numeric_seizure_free_duration, seizure_free_overreach, temporal_conflict |
| 2932 | seizure free for 9 month | seizure free for multiple year | seizure free for 9 months | cluster_or_diary, numeric_seizure_free_duration, seizure_free_overreach, temporal_conflict |
| 2938 | seizure free for 8 month | seizure free for multiple year | seizure free for 8 months | cluster_or_diary, numeric_seizure_free_duration, seizure_free_overreach, temporal_conflict |
| 3469 | unknown | seizure free for multiple year | seizure free for 6 months | cluster_or_diary, temporal_conflict, unknown_no_reference_boundary |

All four are wrong-to-wrong changes, but they expose a real risk: month-bucket
duration selection can make a more specific seizure-free label look more
confident in rows where the note also has temporal conflict, cluster/diary
structure, or a boundary answer.

Decision: a narrower diagnostic gate can block the four residual regression
changes without losing the 18 target corrections if it refuses month-bucket
duration replacement on rows marked `unknown_no_reference_boundary` or
`seizure_free_overreach`. The equivalent hard-slice rule
`temporal_conflict` + `cluster_or_diary` also blocks all four and preserves all
18 target corrections on this artifact.

Research caveat: these are validation hard-slice tags, not production graph
metadata. Do not promote this as a production projection gate until the graph
itself exposes source-near risk features such as active unknown boundary nodes,
competing current frequency nodes, cluster-axis nodes, or explicit temporal
conflict. The correct next ablation is a graph-metadata gate, not a row-tag
gate.

## LLM-Heavy V1 Failure Families

`llm_heavy_clinical_frequency_reasoner_v1` validation250 remains rejected as an
LLM-heavy final-label candidate:

- Structured parse/schema rows: 237/250; parse-schema failures: 13/250.
- Evidence exactness failures: 26/250; event extraction status failures: 38/250.
- Selected-event trace mismatches: 9/250.
- Raw scorer-format failures: 37/250.
- Raw/format-only Purist: 188/250.
- Selected-evidence arithmetic Purist: 219/250, attribution-diagnostic only.

Parse/schema tail:

- 12 schema-validation failures and 1 invalid JSON row.
- Repeated schema failures came from enum drift in `vague_count`, non-dict
  `clinical_quantity`, and an out-of-enum assertion status.
- This is a prompt/schema-contract failure family, not a scoring-policy issue.

Evidence and trace failures:

- 25 invalid event-evidence errors.
- 7 invalid selected-evidence errors.
- 1 row where selected evidence was valid text but not exactly one selected
  event evidence value.
- 9 selected-event trace mismatches where `selection.selected_event_ids` and
  `final_answer.selected_event_ids` diverged.

Raw-label error families:

- 37 raw rows were unscorable, usually because the model put cluster modifiers,
  multiple clauses, or prose-like quantities into `raw_llm_final_label`.
- 11 rows had arithmetic-correct selected evidence but wrong raw rendering;
  examples include bimonthly mapped as `2 per month`, cluster-axis labels
  flattened to ordinary frequency, and compact interval inversions such as
  `2 to 3 per week` instead of `1 per 2 to 3 week`.
- 13 rows were selection or benchmark-mapping errors where arithmetic did not
  rescue the answer; examples include adding cluster burdens incorrectly,
  converting vague `several` to exact counts, and choosing seizure-free or
  conditional/perimenstrual quantities where Gan expects unknown or a different
  current burden.
- 1 row had both raw and arithmetic wrong with different labels, reflecting a
  selected-event trace/selection inconsistency.

Decision: do not escalate v1. A v2 LLM-heavy prompt must first pass a smaller
25/50 ladder with explicit fixes for strict schema enums, final-label grammar,
selected-event trace equality, exact selected evidence copying, bimonthly and
compact interval semantics, cluster-axis preservation, vague-count handling,
and conditional/perimenstrual boundary answers.

## Next Useful Work

1. Implement a diagnostic graph-metadata gate for month-bucket duration
   projection and replay it against the same broad regression panel. The gate
   should use graph features, not validation row tags.
2. Design LLM-replacement ablations for deterministic post-processing modules,
   with score, repair attribution, evidence validity, and replay variance
   reported for each layer.
3. Treat LLM-heavy v2 as a redesign, not a continuation run. It should start at
   validation25 and must show schema/evidence/trace robustness before another
   validation250.
