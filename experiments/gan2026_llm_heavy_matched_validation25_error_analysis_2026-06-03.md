# Gan 2026 LLM-Heavy Matched Validation25 Error Analysis

- Date: 2026-06-03
- Artifact A: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl`
- Artifact B: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Surface: matched first 25 validation rows under `gan2026_split_v1`; no test rows inspected
- Mode: saved artifact analysis; no hosted calls
- Primary comparison: A `raw_llm` versus B `mechanical_adapter_label`; side-car layers reported separately

## Executive Finding

Decision 0006 v2 is stronger as a raw end-to-end LLM renderer on this smoke surface: 22/25 Purist raw and 23/25 raw scorable, with 25/25 if allowed to use deterministic selected-evidence arithmetic. Decision 0007 v0 makes the architectural boundary cleaner by forcing typed selected facts and operands before deterministic rendering, but the v0 contract underperformed: 19/25 mechanical-adapter Purist, 19/25 exact selected evidence, 22/25 complete operands, and 0/25 raw parser labels scorable.

The important difference is not just score. A asks the LLM to satisfy a large JSON schema and render the final Gan label itself, then validates after the fact. B constrains the model through typed DSPy fields and moves final label rendering into deterministic adapters, which is attribution-cleaner, but only works when the model exposes complete, consistent operands and exact evidence.

## Matched Metrics

| Measure | Decision 0006 v2 compact | Decision 0007 v0 adapters |
|---|---:|---:|
| Structured/typed records | 25/25 (1.000) | 25/25 (1.000) |
| Selected evidence exact | 22/25 (0.880) | 19/25 (0.760) |
| Raw parser-label scorable | 23/25 (0.920) | 0/25 (0.000) |
| Raw parser-label Purist | 22/25 (0.880) | 0/25 (0.000) |
| Primary adapted layer scorable | 25/25 (1.000) | 22/25 (0.880) |
| Primary adapted layer Purist | 25/25 (1.000) | 19/25 (0.760) |
| Benchmark/convention side-car Purist | 23/25 (0.920) | 19/25 (0.760) |
| Pragmatic primary adapted | 25/25 (1.000) | 20/25 (0.800) |

## Matched Slice Comparison

| Slice | Rows | A raw Purist | A selected-evidence arithmetic Purist | B mechanical-adapter Purist | Notes |
|---|---:|---:|---:|---:|---|
| all matched validation25 | 25 | 22/25 | 25/25 | 19/25 |  |
| exact selected evidence in both | 16 | 14/16 | 16/16 | 14/16 |  |
| evidence exactness failure in either | 9 | 8/9 | 9/9 | 5/9 | B had most failures from Unicode/control-character evidence copying. |
| upper-bound or inequality rows | 6 | 6/6 | 6/6 | 4/6 | A learned most upper-bound rendering; B often omitted lower bound/inequality semantics. |
| cluster-related rows | 3 | 2/3 | 3/3 | 0/3 | Both still confuse cluster cadence vs event burden; B makes the axis error more visible. |
| vague-count rows | 4 | 3/4 | 4/4 | 2/4 |  |
| raw v2 needs arithmetic side-car | 3 | 0/3 | 3/3 | 2/3 | These are attribution-sensitive: A is not raw-LLM-correct but selected evidence enables deterministic recovery. |
| Decision 0007 operand incomplete/unscorable | 3 | 3/3 | 3/3 | 0/3 | Adapter cannot rescue missing operands by design. |

## Failure Families

Decision 0006 v2 compact (`raw_llm` family):
- `clean_raw_purist`: 20
- `nonselected_event_evidence_not_exact`: 2
- `raw_rendering_or_selection_wrong_but_arithmetic_recovers`: 1
- `selected_evidence_not_exact`: 1
- `raw_parser_label_unscorable`: 1

Decision 0007 v0 adapters (`mechanical_adapter_label` family):
- `clean_adapter_purist`: 15
- `selected_evidence_not_exact`: 6
- `cluster_axis_or_cluster_rendering_wrong`: 2
- `operand_incomplete:incomplete_cluster_operands`: 1
- `vague_count_operand_wrong`: 1

## Row-Level Delta Table

| Pos | Source | Gold | A raw -> arithmetic | B mechanical | Delta / failure read |
|---:|---:|---|---|---|---|
| 1 | 10 | `4 per day` | `4 per day (ok) -> 4 per day (ok)` | `UNSCORABLE (miss)` | A wins; B `selected_evidence_not_exact` |
| 2 | 40 | `4 per week` | `4 per week (ok) -> 4 per week (ok)` | `0 to 4 per 1 week (ok)` | both primary paths correct |
| 3 | 79 | `6 to 7 per year` | `6 to 7 per year (ok) -> 6 to 7 per year (ok)` | `6 to 7 per 1 year (ok)` | both primary paths correct |
| 4 | 103 | `2 to 4 per year` | `2 to 4 per year (ok) -> 2 to 4 per year (ok)` | `2 to 4 per 1 year (ok)` | both primary paths correct |
| 5 | 128 | `17 per month` | `17 per month (ok) -> 17 per month (ok)` | `UNSCORABLE (miss)` | A wins; B `operand_incomplete:incomplete_cluster_operands` |
| 6 | 156 | `1 per 6 day` | `1 per 6 day (ok) -> 1 per 6 day (ok)` | `1 per 6 day (ok)` | both primary paths correct |
| 7 | 180 | `1 per 7 day` | `1 per 7 day (ok) -> 1 per 7 day (ok)` | `1 per 7 day (ok)` | both primary paths correct |
| 8 | 182 | `1 per 2 day` | `2 per 2 day (miss) -> 1 per 2 day (ok)` | `1 per 2 day (ok)` | B wins over A raw; A `raw_rendering_or_selection_wrong_but_arithmetic_recovers` |
| 9 | 187 | `1 per 7 to 9 day` | `2 per 63 day with 1 cluster per 7 to 9 day (miss) -> 1 per 7 to 9 day (ok)` | `1 cluster per 7 to 9 day, 2 per cluster (miss)` | A side-car recovers; B `cluster_axis_or_cluster_rendering_wrong` |
| 10 | 190 | `1 per 4 week` | `1 per 4 week (ok) -> 1 per 4 week (ok)` | `1 cluster per 4 week, multiple per cluster (miss)` | A wins; B `cluster_axis_or_cluster_rendering_wrong` |
| 11 | 198 | `1 per 4 week` | `1 per 4 week (ok) -> 1 per 4 week (ok)` | `1 per 4 week (ok)` | both primary paths correct |
| 12 | 212 | `1 per 3 to 4 week` | `1 per 3 to 4 week (ok) -> 1 per 3 to 4 week (ok)` | `1 per 3 to 4 week (ok)` | both primary paths correct |
| 13 | 218 | `1 per 3 week` | `1 per 3 week (ok) -> 1 per 3 week (ok)` | `1 per 3 week (ok)` | both primary paths correct |
| 14 | 243 | `1 per 4 month` | `1 per 4 month (ok) -> 1 per 4 month (ok)` | `1 per 4 month (ok)` | both primary paths correct |
| 15 | 278 | `multiple per week` | `multiple per week (ok) -> multiple per week (ok)` | `multiple per 7 day (ok)` | both primary paths correct |
| 16 | 280 | `multiple per day` | `no seizure frequency reference (ok) -> no seizure frequency reference (ok)` | `2 per 1 day (miss)` | A wins; B `vague_count_operand_wrong` |
| 17 | 338 | `multiple per month` | `many per month (miss) -> no seizure frequency reference (ok)` | `multiple per 1 month (ok)` | B wins over A raw; A `raw_parser_label_unscorable` |
| 18 | 409 | `1 per month` | `1 per month (ok) -> 1 per month (ok)` | `1 per 1 month (ok)` | both primary paths correct |
| 19 | 419 | `2 per year` | `2 per year (ok) -> 2 per year (ok)` | `2 per 1 year (ok)` | both primary paths correct |
| 20 | 446 | `2 per week` | `2 per 7 day (ok) -> 2 per week (ok)` | `UNSCORABLE (miss)` | A wins; B `selected_evidence_not_exact` |
| 21 | 466 | `21 to 28 per month` | `21 to 28 per month (ok) -> 21 to 28 per month (ok)` | `21 to 28 per 1 month (ok)` | both primary paths correct |
| 22 | 467 | `9 per month` | `9 per month (ok) -> 9 per month (ok)` | `9 per 1 month (ok)` | both primary paths correct |
| 23 | 531 | `12 to 30 per 3 month` | `12 to 30 per 3 month (ok) -> 12 to 30 per 3 month (ok)` | `12 to 30 per 1 month (ok)` | both primary paths correct |
| 24 | 598 | `1 per 8 month` | `1 per 8 month (ok) -> 1 per 8 month (ok)` | `1 per 8 month (ok)` | both primary paths correct |
| 25 | 659 | `2 per 4 day` | `2 per 4 day (ok) -> 2 per 4 day (ok)` | `2 per 4 day (ok)` | both primary paths correct |

## Full Error Analysis

### Decision 0006 v2 Compact

- Strength: strong raw parser-compatible rendering on a compact strict JSON prompt. It produced 25/25 structured records and 22/25 raw Purist, with no selected-event trace mismatches.
- Weakness: its best 25/25 layer is selected-evidence arithmetic, a deterministic side-car. Rows 182, 187, and 338 show why raw and side-car attribution must be separated: the selected evidence is useful, but the model-rendered final label is wrong, overly cluster-specific, or parser-incompatible.
- Evidence issue: selected evidence was exact on 22/25, while event-level evidence had 2 invalid nonselected event snippets. This is less harmful for scoring than invalid selected evidence, but it still violates the promised event schema.
- Clinical failure mode: cluster cadence and vague-count/rendering remain brittle. The model can identify a clinically relevant clause while rendering the wrong scorer-facing label.

### Decision 0007 v0 Evidence Selection With Deterministic Adapters

- Strength: 25/25 typed records and a clearer attribution boundary. The final scorer-facing label is produced only from model-selected operands, so deterministic code does not silently choose a different clinical fact.
- Weakness: the v0 contract did not yet force parser-ready raw labels, exact evidence, or complete operands. Raw parser labels were 0/25 scorable because they used diagnostic underscored labels, not Gan grammar.
- Evidence issue: exact selected evidence was 19/25. Most failures are copy-contract problems around inequality glyphs emitted as control-character or normalized forms; this blocks row review even when the clinical fact is right.
- Operand issue: rows 10, 128, and 446 expose incomplete or inconsistent operand packets, so the adapter appropriately refuses to invent missing lower bounds or switch operand families.
- Clinical failure mode: rows 187 and 190 expose the core cluster-axis problem. The model selected cluster cadence, but the rendered scorer axis should be a bare cadence frequency. Row 280 exposes vague-count semantics: `multiple` should be a vague operand, not a numeric lower bound.

## Schema-Enforcement Comparison

| Aspect | Decision 0006 v2 compact | Decision 0007 v0 adapters |
|---|---|---|
| Output shape | One opaque JSON string parsed into Pydantic models with `extra=forbid`. | DSPy typed output fields: `selected_fact`, `operands`, and `raw_model_answer`, then Pydantic validation. |
| Model responsibility | Model owns event extraction, clinical selection, aggregation, final label rendering, operands, and trace. | Model owns clinical fact selection, exact evidence, temporality/assertion, and operands; deterministic adapter owns final label rendering. |
| Enforcement timing | Mostly post-hoc: parse JSON, validate schema, validate selected-event trace/evidence, then score layers. | More pre-structured: JSONAdapter/typed fields constrain output before local validation; adapter refuses missing/inconsistent operand packets. |
| Attribution | Raw layer is clean only when `raw_llm` succeeds; selected-evidence arithmetic and benchmark-aligned layers are deterministic side-cars. | Cleaner intended attribution: mechanical label is deterministic rendering of model-selected operands, but v0 still needs raw-label grammar and evidence fixes. |
| Failure visibility | Wrong rendering can be hidden by selected-evidence arithmetic if layers are conflated. | Missing operands and clinical-kind/operand inconsistency are explicit adapter failures. |
| Main contract gap on this run | Raw model sometimes misrenders selected facts; event evidence exactness not perfect. | Typed selection is present, but exact evidence, lower-bound/inequality operands, cluster axis, vague-count operands, and raw parser grammar were underspecified in v0. |

## Interpretation And Recommendation

Decision 0006 v2 wins the matched smoke comparison on immediate raw performance and on selected-evidence-arithmetic side-car performance. Decision 0007 v0 is the better enforcement direction if the project goal is attribution-clean LLM-heavy extraction, because deterministic rendering is limited to selected operands and cannot silently change the clinical fact. The v0 artifact should be treated as diagnostic/revise, not promoted.

The next Decision 0007 run should use the current v1-style contract changes already reflected in the source: exact Unicode evidence copying, closed raw parser-label grammar, explicit inequality/lower-bound policy, clinical-kind/operand consistency, cluster answer axis, and vague-count routing. Promotion should require at least validation25 parity with v2 raw on schema health and a validation50 gate with no systemic evidence or operand failures.
