# Gan 2026 LLM Component Mechanics Protocol

Date: 2026-06-03

## Purpose

This protocol restarts RQ1/RQ2/RQ4 after the first-pass reports fell back to the
validation-tuned deterministic selector as the default answer. The deterministic
candidate set, deterministic top label, and deterministic precedence policy are
now off the table as research answers for RQ1-RQ4.

They may be used only as:

- frozen comparator;
- safety floor;
- miss-slice source;
- regression-risk reference;
- oracle-gap reference.

The active question is:

```text
Which LLM components generate useful candidates, select clinically decisive
evidence, and project the correct current benchmark-relevant state, and why do
they help or fail on specific rows and hidden families?
```

## Source Artifacts

Use saved replay artifacts only. Do not make fresh model calls for this pass.

- RQ1 candidate matrix:
  `experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`
- RQ2 evidence matrix:
  `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`
- RQ4 projection matrix:
  `experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl`
- Historical first-pass answers, diagnostic only:
  `docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-03.md`,
  `docs/research/gan2026_rq2_evidence_selection_answer_2026-06-03.md`, and
  `docs/research/gan2026_rq4_projection_answer_2026-06-03.md`

## Components Under Test

RQ1 LLM candidate generation:

- `llm_candidate_selector_raw`;
- `llm_selected_state_or_evidence`;
- claim-table candidate/state views when source rows overlap;
- LLM missing-candidate behavior on deterministic-miss slices.

RQ2 LLM evidence selection:

- `hybrid_adjudicator_raw`;
- `llm_candidate_selector_raw`;
- `llm_heavy_selected_fact`;
- `claim_table_final_query`.

RQ4 LLM or graph-assisted projection:

- `llm_heavy_selected_fact`;
- `claim_table_final_query`;
- `boundary_state_priority`;
- `competing_frequency_uncertainty`;
- `lowest_current_frequency`;
- `seizure_free_priority`;
- `graph_gated_month_bucket_duration`;
- `state_graph_projection` only as a graph-policy diagnostic, not as a broad
  replacement policy.

## Row-Level Analysis Requirements

For each major component, inspect examples where it:

- found a gold-relevant state the deterministic candidate set missed;
- selected exact text but failed the clinical state or benchmark projection;
- selected plausible but non-decisive evidence;
- changed a deterministic-correct row incorrectly;
- exposed a candidate/state that a later projection or rendering step lost.

For each example, record:

- source row index;
- gold label;
- hidden-family tags when available;
- component output label or candidate kind;
- selected/generated evidence snippet;
- deterministic baseline status for context only;
- inferred mechanism: generation, evidence selection, state representation,
  projection, rendering, or scorer/gold ambiguity;
- transfer note: plausible mechanism, validation-shaped artifact, or
  instrumentation gap.

## Metrics

Use metrics as supporting evidence only:

- candidate recall, exact-evidence rate, and candidate burden for RQ1;
- exact evidence, source-id validity, supported-label correctness, changed-row
  W->C/C->W accounting, and operand completeness for RQ2;
- projection correctness, W->C/C->W accounting, surface, hidden family, and
  oracle gap for RQ4.

Do not stop at an aggregate table. If a table says the deterministic baseline is
safest, reclassify that as baseline context and continue the LLM mechanism
analysis.

## Stop Rule

The reset pass is answered when it can state one of the following:

- a named LLM component has a mechanistically credible role for candidate
  generation, evidence selection, or projection on named hidden families;
- all tested LLM components are negative for a subproblem, with row-level
  examples explaining why;
- the answer is blocked by missing source ids, missing hidden-family tags,
  missing same-row overlap, or insufficient raw row context.

Any claim remains validation-development only unless a separate frozen
pre-holdout protocol is written and approved.
