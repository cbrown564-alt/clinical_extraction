# Gan 2026 LLM-Heavy Reasoner V0 Validation25 Error Analysis

Date: 2026-06-02

## Scope

- Artifact analyzed: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`.
- Surface: first 25 rows of `gan2026_split_v1` validation.
- Mode: live GPT-4.1 mini run followed by saved-output schema replay after scalar-list shape repair.
- Claim language: validation development error analysis only; not a benchmark or holdout result.
- Comparator: frozen deterministic V1 on the same 25 validation rows, used only to contextualize failure modes.

## Executive Finding

The v0 LLM-heavy reasoner does not pass the Stage A smoke gate. The model usually identifies clinically useful evidence, but the prediction-bearing raw final label is not parser-ready on any row, and exact final-evidence copying fails on 7/25 rows. The strongest score layer, `selected_evidence_arithmetic`, reaches 23/25 Purist only because deterministic code derives a label from the model-selected evidence; that is a useful diagnostic signal, but it is not an LLM-heavy success claim.

Recommended decision: **revise before validation50**. The next revision should constrain final evidence to one copied selected event evidence string and require a parser-ready `raw_llm_final_label` independent of selected-evidence arithmetic.

## Aggregate Attribution

| Layer | Scorable | Purist correct | Pragmatic correct |
| --- | ---: | ---: | ---: |
| `raw_llm` | 0/25 | 0/25 | 0/25 |
| `format_only` | 11/25 | 10/25 | 10/25 |
| `selected_evidence_arithmetic` | 24/25 | 23/25 | 23/25 |
| `benchmark_aligned` | 24/25 | 13/25 | 13/25 |
| `oracle_format_upper_bound` | 11/25 | 10/25 | 10/25 |

Additional contract metrics:

- Structured records after non-semantic schema replay: 24/25.
- Selected evidence exact: 18/25.
- Event evidence exact: 42/47.
- Selected-event trace mismatches: 0/25.
- Frozen deterministic V1 same-row Purist correct: 25/25.

## Failure Family Counts

| Failure family | Rows |
| --- | ---: |
| `contract_ok_on_format_layer` | 8 |
| `event_evidence_not_exact` | 1 |
| `raw_label_requires_arithmetic` | 8 |
| `schema_failure` | 1 |
| `selected_evidence_arithmetic_wrong` | 1 |
| `selected_evidence_not_exact` | 6 |

Interpretation of the main families:

- `raw_label_requires_arithmetic`: the selected evidence is useful, but the raw label includes prose, inequalities, semiology, cluster modifiers, or window notes that the scorer cannot parse.
- `selected_evidence_not_exact`: the final evidence is a concatenation or paraphrase rather than one exact source substring; this fails the evidence stop rule even when arithmetic can recover the label.
- `benchmark_adapter_regression`: broad Gan repair over raw prose changes a correct selected-evidence-derived answer into an incorrect category; this confirms benchmark alignment must be side-car and not the primary layer.
- `schema_failure`: one row still fails schema validation because `vague_count` used a value outside the allowed enum.

## Row-Level Failure Table

| Row | Gold | Family | Raw label | Selected-evidence arithmetic | Benchmark aligned | Evidence issue |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | `4 per day` | `raw_label_requires_arithmetic` | `up to 4 seizures per day, frequent` | `4 per day` | `multiple per day` | none |
| 40 | `4 per week` | `raw_label_requires_arithmetic` | `≤ four seizures per week` | `4 per week` | `multiple per week` | none |
| 79 | `6 to 7 per year` | `selected_evidence_not_exact` | `≤ 6 to 7 per year with occasional clusters around jet lag and sleep loss` | `6 to 7 per year` | `unknown` | selected evidence is not one exact note substring; 2 event evidence string(s) are not e... |
| 103 | `2 to 4 per year` | `raw_label_requires_arithmetic` | `≤ two or four seizures per year` | `2 to 4 per year` | `4 per year` | none |
| 128 | `17 per month` | `raw_label_requires_arithmetic` | `focal aware seizures with occasional focal to bilateral tonic-clonic seizures...` | `17 per month` | `17 per month` | none |
| 156 | `1 per 6 day` | `raw_label_requires_arithmetic` | `focal epilepsy seizures every 6 days` | `1 per 6 day` | `1 per month` | none |
| 180 | `1 per 7 day` | `contract_ok_on_format_layer` | `seizures every 7 days` | `1 per 7 day` | `1 per 7 day` | none |
| 182 | `1 per 2 day` | `contract_ok_on_format_layer` | `seizures every 2 days` | `1 per 2 day` | `1 per 2 day` | none |
| 187 | `1 per 7 to 9 day` | `selected_evidence_not_exact` | `cluster every 7-9 days of focal aware auras; two nocturnal generalised tonic–...` | `1 per 7 to 9 day` | `unknown` | selected evidence is not one exact note substring |
| 190 | `1 per 4 week` | `selected_evidence_not_exact` | `absence clusters every 4 weeks; tonic–clonic seizure free for 5 months` | `1 per 4 week` | `seizure free for 5 month` | selected evidence is not one exact note substring |
| 198 | `1 per 4 week` | `raw_label_requires_arithmetic` | `seizures every 4 weeks, last seizure 10 days ago` | `1 per 4 week` | `1 per month` | none |
| 212 | `1 per 3 to 4 week` | `raw_label_requires_arithmetic` | `ongoing seizures every 3-4 weeks` | `1 per 3 to 4 week` | `no seizure frequency reference` | none |
| 218 | `1 per 3 week` | `contract_ok_on_format_layer` | `seizures every 3 weeks` | `1 per 3 week` | `1 per 3 week` | none |
| 243 | `1 per 4 month` | `contract_ok_on_format_layer` | `seizure every 4 months` | `1 per 4 month` | `1 per 4 month` | none |
| 278 | `multiple per week` | `contract_ok_on_format_layer` | `multiple seizures per week` | `multiple per week` | `multiple per week` | none |
| 280 | `multiple per day` | `schema_failure` | `` | `` | `` | selected evidence is not one exact note substring |
| 338 | `multiple per month` | `selected_evidence_not_exact` | `frequent seizures in past month with clustering after eastbound flights and s...` | `multiple per day` | `unknown` | selected evidence is not one exact note substring |
| 409 | `1 per month` | `raw_label_requires_arithmetic` | `≤ once per month, typically brief focal impaired awareness episodes` | `1 per month` | `multiple per month` | none |
| 419 | `2 per year` | `contract_ok_on_format_layer` | `approximately twice per year` | `2 per year` | `2 per year` | none |
| 446 | `2 per week` | `event_evidence_not_exact` | `up to twice per week` | `2 per week` | `multiple per week` | 3 event evidence string(s) are not exact substrings |
| 466 | `21 to 28 per month` | `contract_ok_on_format_layer` | `21-28 seizures per month` | `21 to 28 per month` | `21 to 28 per month` | none |
| 467 | `9 per month` | `contract_ok_on_format_layer` | `9 seizures per month` | `9 per month` | `9 per month` | none |
| 531 | `12 to 30 per 3 month` | `selected_evidence_arithmetic_wrong` | `12-30 seizures per quarter with clusters typically following nights of interr...` | `unknown` | `unknown` | none |
| 598 | `1 per 8 month` | `selected_evidence_not_exact` | `1 seizure per 8 months` | `2 per 16 month` | `1 per 8 month` | selected evidence is not one exact note substring |
| 659 | `2 per 4 day` | `selected_evidence_not_exact` | `2 seizures per 4 days with clustering around nights following fragmented sleep` | `2 per 4 day` | `unknown` | selected evidence is not one exact note substring |

## Evidence Contract Failures

The selected-event trace is stable, but final evidence exactness is not. Most failures are concatenated spans or copied sentence fragments that do not exactly match the note text. The prompt should make `final_answer.selected_evidence` copy exactly one selected event `evidence` value, not synthesize a combined justification span.

| Row | Evidence issue | Selected evidence excerpt |
| ---: | --- | --- |
| 79 | selected evidence is not one exact note substring; 2 event evidence string(s) are not exact substrings | seizure frequency currently reported as ≤ 6 to 7 per year, typically clustering around periods of jet lag and sleep loss related to frequent business travel |
| 187 | selected evidence is not one exact note substring | Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days. Over the same interval, there have been two nocturnal generalised tonic–clon... |
| 190 | selected evidence is not one exact note substring | he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days; His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation,... |
| 280 | selected evidence is not one exact note substring |  |
| 338 | selected evidence is not one exact note substring | Over the last four weeks he has experienced many convulsions in past month; These events clustered after eastbound flights and consecutive nights of restricted sleep (3–4 hours) |
| 446 | 3 event evidence string(s) are not exact substrings | Over the past month, the overall frequency has been ≤ twice per week |
| 598 | selected evidence is not one exact note substring | Safety counselling reinforced; patient has self-reported seizure frequency averaging 1 per eight months. Over the past 16 months he has experienced two events, giving an average... |
| 659 | selected evidence is not one exact note substring | She reports that the frequency is consistent at seizures twice every 4 days and clustering around nights following particularly fragmented sleep |

## Semantic And Attribution Errors

Only one scorable selected-evidence-arithmetic row is wrong: row 531. The model selects the right current quarterly burden, but its final evidence/label includes a cluster modifier. The arithmetic derivation falls back to `unknown` instead of preserving `12 to 30 per 3 month`. This is not a clinical selection failure so much as an evidence-to-label derivation brittleness case.

| Row | Gold | Arithmetic label | Raw label | Selected evidence excerpt |
| ---: | --- | --- | --- | --- |
| 531 | `12 to 30 per 3 month` | `unknown` | `12-30 seizures per quarter with clusters typically following nights of interrupted rest` | Current estimated seizure frequency is 12 to 30 per quarter, with clusters typically following nights of interrupted rest |

Benchmark-aligned repair regresses 10 rows that selected-evidence arithmetic gets right. These are mostly inequalities, prose labels, cluster-vs-rate mixtures, or seizure-free distractors in raw labels. This argues against using broad benchmark repair as the primary score layer for this architecture.

| Row | Gold | Arithmetic label | Benchmark-aligned label | Raw label |
| ---: | --- | --- | --- | --- |
| 10 | `4 per day` | `4 per day` | `multiple per day` | `up to 4 seizures per day, frequent` |
| 40 | `4 per week` | `4 per week` | `multiple per week` | `≤ four seizures per week` |
| 79 | `6 to 7 per year` | `6 to 7 per year` | `unknown` | `≤ 6 to 7 per year with occasional clusters around jet lag and sleep loss` |
| 156 | `1 per 6 day` | `1 per 6 day` | `1 per month` | `focal epilepsy seizures every 6 days` |
| 187 | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `unknown` | `cluster every 7-9 days of focal aware auras; two nocturnal generalised tonic–clonic seizures; rare daytime focal impaired aware...` |
| 190 | `1 per 4 week` | `1 per 4 week` | `seizure free for 5 month` | `absence clusters every 4 weeks; tonic–clonic seizure free for 5 months` |
| 212 | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `no seizure frequency reference` | `ongoing seizures every 3-4 weeks` |
| 409 | `1 per month` | `1 per month` | `multiple per month` | `≤ once per month, typically brief focal impaired awareness episodes` |
| 446 | `2 per week` | `2 per week` | `multiple per week` | `up to twice per week` |
| 659 | `2 per 4 day` | `2 per 4 day` | `unknown` | `2 seizures per 4 days with clustering around nights following fragmented sleep` |

## Prompt/Schema Revision Targets

1. Make `final_answer.selected_evidence` an exact copy of one selected event evidence value. If multiple events are selected, add a separate `supporting_event_ids` or `combined_rationale`; do not concatenate evidence strings.
2. Split the final label into `raw_clinical_summary` and `raw_llm_final_label`. The former may contain prose; the latter must be parser-ready, for example `4 per day`, `1 per 7 to 9 day`, or `unknown`.
3. Add explicit examples for inequalities and upper bounds: `≤ four per week` should render as `4 per week`, not `multiple per week` or prose with an inequality symbol.
4. Prevent seizure-free distractor leakage in final labels when a current quantified non-tonic-clonic seizure frequency is selected.
5. Broaden schema alias repair only for non-semantic shape issues, such as singleton enum lists and `vague_count=many -> multiple`; keep selected-event and semantic-kind changes out of repair.

## Decision

Keep `llm_heavy_clinical_frequency_reasoner_v0` as **revise-only**. Do not escalate to validation50 until a same-surface saved-output or fresh validation25 smoke reaches the Stage A stop rule: at least 24/25 schema-valid rows and at least 22/25 exact selected evidence, with raw or format-only labels no longer dominated by deterministic selected-evidence arithmetic.

## Artifacts

- Row-level CSV: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.csv`
- Machine-readable summary: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.json`
- Source JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`
