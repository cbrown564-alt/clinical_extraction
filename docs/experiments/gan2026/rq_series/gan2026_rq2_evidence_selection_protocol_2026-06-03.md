> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ2 Evidence-Selection Protocol

Date: 2026-06-03

Scope: validation-development protocol for RQ2, evidence selection. This is a
component question, not a whole-pipeline promotion or holdout-transfer claim.

## Question

Given the note and a fixed candidate or state substrate, which component best
selects the prediction-bearing evidence span?

Primary component under test: `evidence_selection`.

Fixed comparison component: deterministic selected evidence from
`rules_only_v1` / `deterministic_top_candidate`, with state-graph projection as
the deterministic representability comparator where available.

Surface: saved validation replay artifacts under `gan2026_split_v1`. Locked
holdout artifacts are excluded from this protocol.

## Artifacts To Replay

Replay saved artifacts before making any new model calls:

- `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_replay_2026-06-03.jsonl`
- `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl`
- `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.jsonl`

These compare deterministic top evidence, state-graph projection evidence,
hybrid adjudicator selected evidence, LLM candidate-selector evidence, LLM-heavy
typed selected-fact evidence, and claim-table final-query evidence.

## Matrix Schema

Create one row per `source_row_index`, artifact, and component evidence
decision with these fields:

- source row, split, split manifest, distribution, artifact path;
- candidate name, component owner, selected evidence, source ids;
- evidence status: exact, source-near, invalid, missing, or not applicable;
- selected-source-id validity when the artifact records source ids;
- candidate label, gold label, scorable status, Purist/Pragmatic correctness;
- selected operand completeness when typed operands exist;
- changed-from-deterministic, wrong-to-correct, and correct-to-wrong when the
  row can be compared to the deterministic top layer;
- hidden-family tags from the hidden-family atlas when available.

## Primary Metrics

- Exact selected-evidence rate.
- Selected-source-id validity rate where source ids are instrumented.
- Scorable and Purist-correct rates for the label supported by the selected
  evidence.
- Operand completeness for typed selected-fact evidence.
- Changed-row exact-evidence rate, wrong-to-correct count, and correct-to-wrong
  count against deterministic top evidence.
- Hidden-family exactness and correctness readouts.

## Evidence And Source-Id Requirements

Exact evidence means an artifact-provided selected evidence span is an exact
substring of the source note, or the artifact has already recorded
`selected_evidence_valid: true` / `selected_evidence_exact: true` under the same
source row. Source-near evidence is diagnostic only. Missing evidence cannot
support an RQ2 component claim.

Source-id validity is credited only when the artifact records a selected source
id or selected event/node id. Components without source-id instrumentation are
reported separately rather than treated as valid.

## Stop Rule

RQ2 can be marked answered for validation development when the report can state:

- which component should be the default selected-evidence source;
- whether LLM-owned evidence selection adds reliable selective value;
- which evidence-selection failures are actually projection, rendering, schema,
  or candidate-generation failures for later RQs;
- what instrumentation prevents a stronger claim.

If source-id or evidence-span instrumentation is missing for a major component,
the answer must be bounded as development-only or diagnostic.

## Disallowed Work

- No locked-test row-level inspection or tuning.
- No new model calls until saved validation artifacts have been replayed.
- No final F1-only answer; whole-pipeline score layers can contextualize
  evidence decisions but cannot replace evidence-selection metrics.
- No LLM-superiority claim without exact changed-row evidence and deterministic
  correct-regression accounting.
