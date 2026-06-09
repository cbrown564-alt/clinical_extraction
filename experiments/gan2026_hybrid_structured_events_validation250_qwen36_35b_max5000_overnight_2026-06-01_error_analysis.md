# Gan 2026 Qwen Structured-Events Validation250 Error Analysis

Date: 2026-06-02

Analyzed artifact: `experiments/gan2026_llm_only_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.md`

JSONL inspected: `experiments/gan2026_llm_only_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`

This is an error analysis of a validation development run, not a held-out benchmark result.

## Executive Read

The reported purist score, 152 / 250 = 0.608, is dominated by a format failure rather than a clinical extraction failure.

Of the 98 purist errors, 83 are strict JSON parse failures. Every one of those 83 raw outputs is a Python-literal style object with single-quoted keys/strings, and 55 also contain Python `None`. If those 83 outputs are converted with an oracle format-only pass (`ast.literal_eval` followed by `json.dumps`) and then sent through the existing deterministic repair stack, 79 / 83 become purist-correct.

That gives a useful two-layer interpretation:

| View | Purist correct | Accuracy | Main meaning |
| --- | ---: | ---: | --- |
| As scored | 152 / 250 | 0.608 | Strict end-to-end pipeline result |
| Structured rows only | 152 / 167 | 0.910 | Clinical/repair quality when parse succeeds |
| Oracle format-only salvage | 231 / 250 | 0.924 | Approximate content quality if Python-literal outputs were accepted |

The practical conclusion is that the run is primarily a Qwen/Ollama structured-output compliance failure. The clinical content is much stronger than the scored metric suggests, but the deployed pipeline cannot rely on that unless parsing is repaired or generation is constrained.

## Error Budget

| Bucket | Count | Share of all rows | Share of as-scored errors |
| --- | ---: | ---: | ---: |
| Correct as scored | 152 | 60.8% | n/a |
| Invalid JSON parse failures | 83 | 33.2% | 84.7% |
| Structured but purist-wrong | 15 | 6.0% | 15.3% |
| Total purist-wrong as scored | 98 | 39.2% | 100.0% |

After oracle format salvage:

| Bucket | Count |
| --- | ---: |
| Invalid JSON rows salvageable to structured records | 83 / 83 |
| Salvaged rows purist-correct | 79 / 83 |
| Salvaged rows still purist-wrong | 4 / 83 |
| Total content-level purist errors after salvage | 19 / 250 |

Evidence exact-substring validity follows the same pattern:

| View | Exact evidence substrings |
| --- | ---: |
| As scored | 151 / 250 |
| Structured rows only | 151 / 167 |
| Oracle format salvage | 223 / 250 |
| Salvaged invalid rows only | 72 / 83 |

## Format Failure Diagnosis

All 83 parse failures have the same parser symptom:

`invalid_json: Expecting property name enclosed in double quotes`

Raw-output pattern counts:

| Pattern | Count |
| --- | ---: |
| Python literal with single-quoted keys/strings | 83 |
| Python `None` literal present | 55 |
| Markdown fenced output | 0 |
| Python booleans present | 0 |

Representative example: row 10 emits `{'events': ... 'notes': None ...}` rather than strict JSON. Clinically, it selects `<= 4 per day` for a gold label of `4 per day`; the existing label repair would make this correct if the parser accepted the object.

Interpretation: the prompt instruction "Return exactly one JSON object with no markdown" is insufficient for this model/provider path. The issue is not truncation, call failure, or schema complexity alone. It is a systematic serialization dialect failure.

## Distribution of Parse Failures

Parse failures are spread across clinical categories, but they disproportionately harm frequent and unknown/unresolved rows because those are common in the sample.

By gold kind:

| Gold kind | Total rows | Invalid JSON |
| --- | ---: | ---: |
| frequency | 167 | 54 |
| unresolved_multiple | 21 | 12 |
| unknown | 24 | 10 |
| seizure_free | 38 | 7 |

By purist gold category:

| Gold category | Total rows | Invalid JSON | As-scored correct | Oracle-format correct |
| --- | ---: | ---: | ---: | ---: |
| seizure_freq_1ormore_daily | 22 | 11 | 11 | 22 |
| seizure_freq_more1week_less1day | 64 | 22 | 41 | 61 |
| seizure_freq_more1mon_less1week | 34 | 9 | 22 | 30 |
| seizure_freq_more1per6mon_less1mon | 20 | 4 | 16 | 20 |
| seizure_freq_1_per_mon | 16 | 5 | 9 | 13 |
| seizure_freq_1_per_week | 6 | 3 | 2 | 5 |
| seizure_freq_1_per_6mon | 2 | 0 | 2 | 2 |
| seizure_freq_1_per_yr | 3 | 0 | 3 | 3 |
| currently_no_seizure | 38 | 7 | 27 | 34 |
| seizure_freq_unknown | 45 | 22 | 19 | 41 |

## Structured-Row Clinical Errors

Among the 167 successfully parsed rows, 15 are purist-wrong. These are the clinically meaningful errors in the scored structured subset.

Top structured-row purist confusions:

| Gold category | Predicted category | Count |
| --- | --- | ---: |
| seizure_freq_unknown | currently_no_seizure | 3 |
| currently_no_seizure | seizure_freq_1_per_yr | 2 |
| seizure_freq_1_per_mon | seizure_freq_more1per6mon_less1mon | 1 |
| seizure_freq_more1mon_less1week | seizure_freq_1_per_mon | 1 |
| seizure_freq_1_per_week | seizure_freq_unknown | 1 |
| seizure_freq_more1week_less1day | seizure_freq_1_per_week | 1 |
| currently_no_seizure | seizure_freq_more1week_less1day | 1 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 1 |
| seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 1 |
| currently_no_seizure | seizure_freq_more1per6mon_less1mon | 1 |
| seizure_freq_unknown | seizure_freq_more1mon_less1week | 1 |
| seizure_freq_1_per_mon | currently_no_seizure | 1 |

Kind-level mismatches or same-kind misnormalizations among the 15:

| Gold kind | Predicted final kind | Count |
| --- | --- | ---: |
| frequency | frequency | 4 |
| seizure_free | seizure_free | 4 |
| frequency | unknown | 2 |
| unknown | seizure_free | 2 |
| unresolved_multiple | seizure_free | 1 |
| unknown | frequency | 1 |
| frequency | seizure_free | 1 |

Heuristic clinical themes in the 15 structured errors are overlapping, not mutually exclusive:

| Theme | Count |
| --- | ---: |
| relative-window/date/count reasoning | 15 |
| medication/distractor-rich context | 15 |
| multiple semiologies | 14 |
| unknown/no-reference boundary | 11 |
| cluster structure | 9 |
| seizure-free duration or dated anchor | 8 |

## High-Value Structured Error Rows

| Row | Gold | Prediction | Failure mode |
| ---: | --- | --- | --- |
| 816 | `1 per month` | `4 per 10 month` | Temporal repair over-derived from "4 in 2017" despite monthly wording. Pragmatic-correct but purist-wrong. |
| 1030 | `1 to 3 per month` | `1 per month` | Range phrase "one or three seizures last month" collapsed to lower bucket. |
| 1046 | `3 to 5 per month` | `unknown` | Model identified evidence but refused to normalize uncertain reporter phrasing. |
| 1695 | `multiple per month` | `seizure free for multiple year` | Selected current-month absence of events over active clustered burden. |
| 2023 | `5 per month` | `4 per month` | Failed to add four absence seizures plus one myoclonic seizure. |
| 2932 | `seizure free for 9 month` | `13 per 2 month` | Repair stack replaced correct seizure-free selection with dated-sequence frequency. |
| 2992 | `seizure free for 7 month` | `1 per 8 month` | Repair stack transformed seizure-free since-date evidence into sparse frequency. |
| 3015 | `seizure free for 12 month` | `1 per 13 month` | Same seizure-free-to-frequency repair failure. |
| 3371 | `unknown` | `seizure free for multiple year` | "No events in past eight weeks" overinterpreted as seizure-free benchmark label despite gold unknown. |
| 3534 | `unknown` | `seizure free for 7 month` | "Better" and no rescue/injuries converted to seizure-free. |
| 4173 | `1 per 2 week` | `no seizure frequency reference` | Fortnight expression was selected but repair converted it to no-reference. |
| 4368 | `5 per 2 month` | `5 per month` | Event-date list counted correctly but window inferred too narrowly. |
| 4839 | `seizure free for multiple month` | `1 per 5 month` | Seizure-free duration converted into sparse frequency. |
| 5491 | `unknown` | `2 per 6 week` | Peer-reported episodes treated as countable gold frequency though gold policy is unknown. |
| 5528 | `1 per month` | `seizure free for multiple year` | "No additional episodes" selected over the relevant recurring event. |

## Salvaged-But-Still-Wrong Rows

Only 4 of the 83 parser-blocked rows remain purist-wrong after oracle format repair:

| Row | Gold | Salvaged prediction | Failure mode |
| ---: | --- | --- | --- |
| 1165 | `5 to 7 per 3 week` | `seizure free for multiple year` | Selected later no-events window over recent cluster burden. |
| 2459 | `7 to 9 per 2 week` | `5 per 5 month` | Initially selected correct fortnight count, then repair overrode it using dated/event-list logic. |
| 2548 | `5 to 6 per 2 month` | `multiple per week` | Arithmetic/labeling error: model says 5-6 over two months but rationale calls it multiple per week. |
| 4337 | `3 per 3 month` | `no seizure frequency reference` | Event-date list was detected, but repair rejected/overrode the count. |

These four reinforce that after strict-format repair, the remaining weaknesses are not broad extraction failure. They are temporal-window selection, count/window arithmetic, and over-aggressive deterministic repair.

## Deterministic Repair Effects

The run contains 109 final-label repair transformations across 105 rows. Many are beneficial format normalizations, for example plural-to-singular unit repair or removing leading `<=`. But several clinical errors are caused or worsened by repair layers.

Most common repair:

| Repair | Count |
| --- | ---: |
| `seizure free` -> `seizure free for multiple year` | 16 |

Risky repair families observed:

| Pattern | Example rows | Risk |
| --- | --- | --- |
| Seizure-free converted to sparse frequency | 2932, 2992, 3015, 4839 | Dated last-event evidence can be mistaken for a rate. |
| Correct recent count overwritten by dated/event-list repair | 2459, 4337 | Repair stack may prefer a lower-confidence derived label over selected evidence. |
| Idiom repair failure | 4173 | `1 per fortnight` should become `1 per 2 week`, not no-reference. |
| Count-list window inference | 4368 | Event list count is right but denominator/window is wrong. |
| Vague-count policy boundary | 338, 2149, 4732, 4771, 5507 | "occasional", "infrequent", "since June" often collapse to no-reference/unknown policy states. |

The repair stack is a net positive for this run, but it needs precedence rules: do not override a parseable selected final label with a derived label unless the derived label has stronger evidence and passes semantic compatibility checks.

## Main Failure Families

1. Strict JSON compliance

This is the largest and most actionable issue. The parser currently discards clinically useful outputs because Qwen returns Python-literal syntax. This alone accounts for 83 rows and 79 otherwise-correct predictions.

2. Seizure-free versus frequency temporal precedence

Rows 1165, 1695, 2932, 2992, 3015, 3371, 3534, 4839, and 5528 show variants of the same boundary: a no-events interval, a dated last event, or an "otherwise well" statement competes with current/recent count evidence. Sometimes the LLM chooses the wrong clinical state; sometimes deterministic repair corrupts the right state.

3. Count/window arithmetic

Rows 2023, 2459, 2548, 4337, and 4368 show failures to combine counts, preserve the stated denominator, or infer the correct window from event lists. These are small in count but high value because the model often extracts the right evidence.

4. Unknown/no-reference policy boundary

Rows 3371, 3534, 5491, and several scorer-correct semantic mismatches show that the model/repair stack is still mixing benchmark policy states: unknown, no-reference, unresolved multiple, and seizure-free. This matters even when the purist category sometimes masks the semantic difference.

5. Idioms and source-near phrases

`fortnight`, `one or three`, `five to six over two months`, and qualitative expressions like `occasional` need explicit normalization policy. The model frequently captures the phrase but either self-normalizes incorrectly or gets overruled by repair.

## Recommendations

1. Add a bounded Python-literal fallback parser before declaring `invalid_json`.

For this exact artifact, `ast.literal_eval(raw_output)` followed by the existing schema validation would recover all 83 parse-failed rows and 79 correct predictions. This should be guarded and logged as `python_literal_json_repair`, not silently treated as strict JSON.

2. Add tests for Qwen-style single-quote/`None` outputs.

The test should assert that row-like payloads with `{'events': ..., 'notes': None}` are converted, schema-validated, and scored exactly like strict JSON.

3. Make repair precedence conservative.

If the selected final label is parseable and the selected evidence is an exact substring, derived repair families should not overwrite it unless they explicitly prove a higher-priority policy case. In particular, seizure-free labels should not be rewritten into sparse frequencies by dated-sequence or elapsed-anchor repair.

4. Add targeted fixtures for the 19 content-level error rows.

Prioritize rows 1165, 1695, 2023, 2459, 2932, 2992, 3015, 4173, 4337, 4368, 4839, 5491, and 5528. These cover the remaining real weaknesses after format salvage.

5. Report two metrics for local open-model runs.

Keep the strict end-to-end score, but add a "format-repaired content score" when the raw output can be safely coerced and schema-validated. For this run, that distinction is 0.608 versus 0.924, which is too large to hide in a single headline number.

## Bottom Line

This run should not be read as "Qwen 35B only reaches 60.8% on the task." It should be read as "the current Qwen/Ollama structured-output path is unreliable under a strict JSON parser; when formatting is repaired, the content is approximately 92.4% purist-correct on this validation slice."

The next engineering move is therefore not prompt tuning for clinical reasoning. It is robust structured-output recovery plus a small repair-stack hardening pass for seizure-free/date/count precedence.
