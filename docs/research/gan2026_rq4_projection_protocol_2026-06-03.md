# Gan 2026 RQ4 Projection Protocol

Date: 2026-06-03

Scope: validation-development protocol for RQ4, projection. This is a
component question, not a whole-pipeline promotion or holdout-transfer claim.

## Question

Given fixed candidates/states and selected evidence, which projection component
best converts the selected clinical state into the scorer-facing Gan label
without changing the clinical fact?

Primary component under test: `projection`.

Fixed comparison component: `deterministic_top_candidate` from the saved hybrid
parallel state-candidate reasoner validation replay.

Surface: saved validation replay and preexisting diagnostic state-graph
projection ablations under `gan2026_split_v1`. Locked holdout artifacts are
excluded.

## Artifacts To Replay

Replay saved artifacts before making any new model calls:

- `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`
- `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.jsonl`
- `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.jsonl`

The first artifact gives same-row validation750 comparisons among
deterministic top, state graph projection, hybrid adjudicator raw selection, and
diagnostic LLM/schema projections. The second and third artifacts isolate graph
projection policy behavior on representable hard slices and seizure-free
duration rows.

## Compared Projection Components

| Component | RQ4 role |
| --- | --- |
| `deterministic_top_candidate` | Frozen transparent default projection/selection comparator. |
| `state_graph_projection` | Broad graph projection policy over fixed graph nodes. |
| `hybrid_adjudicator_raw` | LLM adjudicator final selected state/label over deterministic and graph candidates. |
| `claim_table_final_query` | Claim-table final query on validation25/250 diagnostic surfaces. |
| `llm_heavy_selected_fact` | LLM-heavy selected fact with deterministic adapter on validation250. |
| `boundary_state_priority` | Diagnostic graph policy for unknown/unresolved-multiple boundary states. |
| `graph_gated_month_bucket_duration` | Diagnostic graph-gated seizure-free duration projection policy. |
| `oracle_gold_node` | Gold-aware upper bound; never a promotable policy. |

## Matrix Schema

Create one row per source row and projection decision with these fields:

- source row, split/distribution surface, artifact path;
- component name, component owner, projection policy;
- candidate label, deterministic baseline label, gold label;
- projection correctness using saved Purist correctness or exact diagnostic
  correctness, depending on surface;
- changed-from-baseline, wrong-to-correct, and correct-to-wrong accounting;
- evidence status and selected source/node-id validity where instrumented;
- hidden-family or diagnostic failure-family tags;
- claim boundary for same-row validation replay versus diagnostic graph replay.

## Primary Metrics

- Projection correctness under the fixed saved surface.
- Changed-row accounting against the deterministic top or graph baseline.
- Wrong-to-correct and correct-to-wrong counts.
- Evidence exactness and selected node/source-id validity for changed rows.
- Hidden-family and diagnostic failure-family readouts.
- Oracle gap on representable graph rows.

## Stop Rule

RQ4 can be marked answered for validation development when the report can state:

- which component remains the safest broad default;
- whether any projection policy has selective value without observed
  deterministic-correct regressions;
- which hidden families remain projection fragile;
- whether a policy is promotable or only diagnostic;
- what schema, evidence, or rendering gaps block a stronger claim.

## Disallowed Work

- No locked-test row-level inspection or tuning.
- No new model calls.
- No aggregate F1-only answer.
- No promotion of graph or LLM projection without exact changed-row evidence,
  deterministic-correct regression accounting, and a frozen pre-holdout policy.
