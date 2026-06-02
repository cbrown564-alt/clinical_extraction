# Gan 2026 LLM-Heavy V2 Validation25 Error Analysis

- Source JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl`
- CSV: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.csv`
- JSON: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.json`
- Split/surface: first 25 `validation` rows from `gan2026_split_v1`.
- Mode: saved-output analysis only; no hosted calls, scorer changes, parser changes, or holdout inspection.
- Claim language: validation development error analysis; not a benchmark result.

## Summary

- Decision: `reject` validation50 escalation remains correct.
- Primary reason: output-contract reliability missed decision 0006 even though raw labels were strong where parseable.
- Raw model-owned Purist: 21/25; raw parser-compatible: 22/25.
- Deterministic selected-evidence arithmetic: 21/25 Purist and corrected 0 raw-wrong rows.
- Selected-event trace mismatches: 0/25.
- Selected evidence exact: 22/25, because the three blocking parse rows had no accepted structured record.

## Failure Families

- `invalid_json_truncation`: 1
- `missing_required_final_answer_field`: 2
- `nonselected_event_evidence_not_exact`: 2
- `wrong_selected_fact_or_cluster_semantics`: 1

## Row-Level Findings

| row | family | gold | raw | selected-evidence arithmetic | issue | next fix |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | `missing_required_final_answer_field` | `4 per day` | `` | `` | schema_validation_error: Field required | Shorten schema and repeat selected_event_ids as a required final_answer field; do not rely on parser fallback in promoted score. |
| 40 | `nonselected_event_evidence_not_exact` | `4 per week` | `4 per week` | `4 per week` | evidence: invalid event evidence for ['sf-5'] | Tell model to omit administrative/no-reference events unless the exact substring is copied; selected answer is otherwise usable. |
| 79 | `invalid_json_truncation` | `6 to 7 per year` | `` | `` | invalid_json: Expecting ',' delimiter | Shorten output contract or raise max_tokens only after predeclaring; current prompt invites overlong rationale/event lists. |
| 128 | `nonselected_event_evidence_not_exact` | `17 per month` | `17 per month` | `17 per month` | evidence: invalid event evidence for ['sf-3'] | Tell model to omit administrative/no-reference events unless the exact substring is copied; selected answer is otherwise usable. |
| 187 | `wrong_selected_fact_or_cluster_semantics` | `1 per 7 to 9 day` | `2 per 7 to 9 day` | `2 per 7 to 9 day` | raw label wrong | Clarify that cluster cadence every N days is one cluster occurrence per interval unless the selected evidence states multiple events per cluster. |
| 659 | `missing_required_final_answer_field` | `2 per 4 day` | `` | `` | schema_validation_error: Field required | Shorten schema and repeat selected_event_ids as a required final_answer field; do not rely on parser fallback in promoted score. |

## Interpretation

This run did not fail because deterministic selected-evidence arithmetic was carrying the model. On every scorable row, the raw, format-only, selected-evidence arithmetic, and benchmark-aligned layers agreed in Purist outcome. The gap is instead a contract and compactness problem: two rows omitted `final_answer.selected_event_ids`, one row was truncated into invalid JSON, and two otherwise-correct rows copied invalid non-selected administrative evidence.

The one substantive label error is row 187. The model selected the right cluster-cadence evidence but converted “events tend to cluster every seven to nine days” into `2 per 7 to 9 day` by importing a separate statement about two nocturnal tonic-clonic seizures. The gold treats the cluster cadence itself as `1 per 7 to 9 day`. A v2 revision should explicitly separate cluster cadence from events-per-cluster unless the selected evidence states the per-cluster burden.

## Recommended Revision Targets

1. Shrink the output schema and cap prose so validation25 cannot truncate at the current token budget.
2. Make `final_answer.selected_event_ids` impossible to omit, ideally near `selected_evidence` in the schema and examples.
3. Tell the model to omit administrative/no-reference events unless exact copied evidence is necessary for the final answer.
4. Add a cluster-cadence instruction: “cluster every N days” means one cluster occurrence per interval unless the same selected evidence states multiple events per cluster.
5. Rerun only validation25 after recording the revised prompt/schema; do not escalate to validation50 from this artifact.
